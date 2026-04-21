from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import logging
from src.config import settings
from src.database import get_db, init_db
from src.models import LinkVisit
from src.schemas import (
    LinkVisitResponse,
    LinkStats,
    DeviceStats,
    TimeSeriesStats
)

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
    logger.info("Starting Analytics Service...")
    init_db()
    logger.info("Analytics Service ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Analytics Service...")


# Tworzenie aplikacji FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="Serwis analityki i statystyk odwiedzin linków",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint sprawdzający stan serwisu"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.api_version
    }


@app.get("/", tags=["root"])
async def root():
    """Główny endpoint z informacjami o API"""
    return {
        "message": "Analytics Service",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/stats/{short_code}", response_model=LinkStats, tags=["stats"])
def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    """
    Pobiera podstawowe statystyki dla danego linku.
    
    - **short_code**: Krótki kod linku
    """
    # Sprawdź czy są jakieś odwiedziny
    visits = db.query(LinkVisit).filter(LinkVisit.short_code == short_code).all()
    
    if not visits:
        raise HTTPException(
            status_code=404,
            detail=f"Brak statystyk dla linku '{short_code}'"
        )
    
    # Oblicz statystyki
    total_visits = len(visits)
    unique_ips = db.query(distinct(LinkVisit.ip_address)).filter(
        LinkVisit.short_code == short_code,
        LinkVisit.ip_address.isnot(None)
    ).count()
    
    # Daty
    first_visit = db.query(func.min(LinkVisit.timestamp)).filter(
        LinkVisit.short_code == short_code
    ).scalar()
    
    last_visit = db.query(func.max(LinkVisit.timestamp)).filter(
        LinkVisit.short_code == short_code
    ).scalar()
    
    return LinkStats(
        short_code=short_code,
        total_visits=total_visits,
        unique_ips=unique_ips,
        first_visit=first_visit,
        last_visit=last_visit
    )


@app.get("/stats/{short_code}/visits", response_model=list[LinkVisitResponse], tags=["stats"])
def get_link_visits(
    short_code: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Pobiera szczegółową listę odwiedzin dla danego linku.
    
    - **short_code**: Krótki kod linku
    - **skip**: Liczba rekordów do pominięcia
    - **limit**: Maksymalna liczba zwracanych rekordów
    """
    visits = db.query(LinkVisit).filter(
        LinkVisit.short_code == short_code
    ).order_by(
        LinkVisit.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    if not visits:
        raise HTTPException(
            status_code=404,
            detail=f"Brak odwiedzin dla linku '{short_code}'"
        )
    
    return visits


@app.get("/stats/{short_code}/devices", response_model=list[DeviceStats], tags=["stats"])
def get_device_stats(short_code: str, db: Session = Depends(get_db)):
    """
    Pobiera statystyki według typu urządzenia.
    
    - **short_code**: Krótki kod linku
    """
    stats = db.query(
        LinkVisit.device_type,
        func.count(LinkVisit.id).label('count')
    ).filter(
        LinkVisit.short_code == short_code
    ).group_by(
        LinkVisit.device_type
    ).all()
    
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Brak statystyk dla linku '{short_code}'"
        )
    
    return [
        DeviceStats(device_type=device_type or "unknown", count=count)
        for device_type, count in stats
    ]


@app.get("/stats/{short_code}/timeseries", response_model=list[TimeSeriesStats], tags=["stats"])
def get_timeseries_stats(
    short_code: str,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Pobiera statystyki w podziale na dni.
    
    - **short_code**: Krótki kod linku
    - **days**: Liczba dni wstecz (domyślnie 7)
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    stats = db.query(
        func.date(LinkVisit.timestamp).label('date'),
        func.count(LinkVisit.id).label('visits')
    ).filter(
        LinkVisit.short_code == short_code,
        LinkVisit.timestamp >= start_date
    ).group_by(
        func.date(LinkVisit.timestamp)
    ).order_by(
        func.date(LinkVisit.timestamp)
    ).all()
    
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Brak statystyk dla linku '{short_code}' w ostatnich {days} dniach"
        )
    
    return [
        TimeSeriesStats(date=str(date), visits=visits)
        for date, visits in stats
    ]


@app.get("/stats", tags=["stats"])
def get_global_stats(db: Session = Depends(get_db)):
    """
    Pobiera globalne statystyki całego systemu.
    """
    total_visits = db.query(func.count(LinkVisit.id)).scalar()
    unique_links = db.query(func.count(distinct(LinkVisit.short_code))).scalar()
    
    # Top 10 najczęściej odwiedzanych linków
    top_links = db.query(
        LinkVisit.short_code,
        func.count(LinkVisit.id).label('visits')
    ).group_by(
        LinkVisit.short_code
    ).order_by(
        func.count(LinkVisit.id).desc()
    ).limit(10).all()
    
    return {
        "total_visits": total_visits,
        "unique_links": unique_links,
        "top_links": [
            {"short_code": code, "visits": visits}
            for code, visits in top_links
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
