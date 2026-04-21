from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from src.core.database import init_db
from src.core.config import settings
from src.api.links import router as links_router

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
    logger.info("Starting Link Management Service...")
    # Baza danych już istnieje, nie trzeba jej tworzyć przy każdym starcie
    # init_db() # Odkomentuj tylko gdy trzeba utworzyć/zaktualizować strukturę
    logger.info("Link Management Service ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Link Management Service...")


# Tworzenie aplikacji FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="Serwis zarządzania skróconymi linkami - CRUD operations",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji ustaw konkretne domeny
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint do sprawdzania stanu serwisu"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.api_version
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Główny endpoint z informacjami o API"""
    return {
        "message": "Link Management Service",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }


# Rejestracja routerów
app.include_router(links_router, prefix="/api/v1/links")


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
