from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LinkVisitCreate(BaseModel):
    """Schema dla tworzenia wpisu odwiedzin"""
    short_code: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None


class LinkVisitResponse(BaseModel):
    """Schema dla odpowiedzi z danymi odwiedzin"""
    id: int
    short_code: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class LinkStats(BaseModel):
    """Schema dla statystyk linku"""
    short_code: str
    total_visits: int
    unique_ips: int
    last_visit: Optional[datetime] = None
    first_visit: Optional[datetime] = None


class DeviceStats(BaseModel):
    """Statystyki według typu urządzenia"""
    device_type: str
    count: int


class TimeSeriesStats(BaseModel):
    """Statystyki w czasie"""
    date: str
    visits: int
