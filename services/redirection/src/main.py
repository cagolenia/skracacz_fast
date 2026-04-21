from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
import httpx
from datetime import datetime
from src.config import settings
from src.cache import cache
from src.queue import message_queue

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Zarządzanie cyklem życia aplikacji"""
    # Startup
    logger.info("Starting Redirection Service...")
    await cache.connect()
    await message_queue.connect()
    logger.info("Redirection Service ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Redirection Service...")
    await cache.disconnect()
    await message_queue.disconnect()


# Tworzenie aplikacji FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="Serwis szybkich przekierowań z cache Redis",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji ustaw konkretne domeny
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware do logowania zapytań
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware logujący każde zapytanie"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint sprawdzający stan serwisu"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.api_version,
        "cache": "connected",
        "queue": "connected"
    }


@app.get("/", tags=["root"])
async def root():
    """Główny endpoint z informacjami o API"""
    return {
        "message": "Redirection Service",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }


async def get_long_url_from_cache(short_code: str) -> str | None:
    """Pobierz długi URL z cache Redis"""
    return await cache.get(f"link:{short_code}")


async def get_long_url_from_api(short_code: str) -> dict | None:
    """Pobierz długi URL z API Link Management (fallback)"""
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            url = f"{settings.link_management_url}/api/v1/links/{short_code}"
            response = await client.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Unexpected response from API: {response.status_code}")
                return None
                
    except httpx.TimeoutException:
        logger.error(f"Timeout while fetching link {short_code} from API")
        return None
    except Exception as e:
        logger.error(f"Error fetching link from API: {e}")
        return None


async def save_to_cache(short_code: str, long_url: str):
    """Zapisz długi URL do cache"""
    await cache.set(f"link:{short_code}", long_url, ttl=settings.redis_ttl)


async def publish_visit_event(short_code: str, request: Request):
    """Publikuj zdarzenie odwiedzenia linku do kolejki"""
    event_data = {
        "short_code": short_code,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "referer": request.headers.get("referer", ""),
    }
    
    await message_queue.publish_event(event_data)


@app.get("/{short_code}", tags=["redirection"])
async def redirect_to_long_url(short_code: str, request: Request):
    """
    Przekierowanie z krótkiego kodu do długiego URL.
    
    Proces:
    1. Sprawdź Redis cache
    2. Jeśli brak - zapytaj Link Management API
    3. Zapisz do cache (jeśli znaleziono)
    4. Wyślij zdarzenie do kolejki analitycznej
    5. Zwróć przekierowanie 301
    """
    
    # Krok 1: Sprawdź cache
    long_url = await get_long_url_from_cache(short_code)
    
    # Krok 2: Fallback do API
    if not long_url:
        logger.info(f"Cache miss for {short_code}, fetching from API")
        link_data = await get_long_url_from_api(short_code)
        
        if not link_data:
            raise HTTPException(
                status_code=404,
                detail=f"Link '{short_code}' nie istnieje lub wygasł"
            )
        
        long_url = link_data.get("long_url")
        
        # Sprawdź czy link jest aktywny
        if not link_data.get("is_active", True):
            raise HTTPException(
                status_code=410,
                detail=f"Link '{short_code}' nie jest już aktywny"
            )
        
        # Krok 3: Zapisz do cache
        await save_to_cache(short_code, long_url)
        logger.info(f"Cached {short_code} -> {long_url}")
    
    # Krok 4: Publikuj zdarzenie do analityki
    try:
        await publish_visit_event(short_code, request)
    except Exception as e:
        # Nie przerywaj przekierowania jeśli wysłanie eventu się nie powiedzie
        logger.error(f"Failed to publish visit event: {e}")
    
    # Krok 5: Przekierowanie
    return RedirectResponse(url=long_url, status_code=301)


@app.delete("/cache/{short_code}", tags=["cache"])
async def invalidate_cache(short_code: str):
    """
    Usuń wpis z cache (do użycia przez Link Management przy aktualizacji/usunięciu)
    """
    await cache.delete(f"link:{short_code}")
    return {"message": f"Cache invalidated for {short_code}"}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Globalny handler wyjątków"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
