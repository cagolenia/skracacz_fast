from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class LinkBase(BaseModel):
    """Bazowy schemat dla linku"""
    long_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkCreate(LinkBase):
    """Schemat do tworzenia nowego linku"""
    pass


class LinkResponse(LinkBase):
    """Schemat odpowiedzi z linkiem"""
    id: int
    short_code: str
    created_at: datetime
    clicks: int = 0
    is_active: bool = True

    class Config:
        from_attributes = True


class LinkVisitEvent(BaseModel):
    """Zdarzenie odwiedzin linku - do kolejki RabbitMQ"""
    short_code: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None


class AnalyticsRecord(BaseModel):
    """Rekord analityczny"""
    link_id: int
    short_code: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None

    class Config:
        from_attributes = True
