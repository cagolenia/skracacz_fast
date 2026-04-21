from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, validator


class LinkCreate(BaseModel):
    """Schemat do tworzenia nowego linku"""
    long_url: str
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=50)
    expires_at: Optional[datetime] = None
    
    @validator('long_url')
    def validate_url(cls, v):
        """Walidacja URL"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL musi zaczynać się od http:// lub https://')
        if len(v) < 10:
            raise ValueError('URL jest za krótki')
        if len(v) > 2048:
            raise ValueError('URL jest za długi (max 2048 znaków)')
        return v
    
    @validator('custom_alias')
    def validate_custom_alias(cls, v):
        """Walidacja własnego aliasu"""
        if v is not None:
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Alias może zawierać tylko litery, cyfry, myślniki i podkreślenia')
        return v


class LinkResponse(BaseModel):
    """Schemat odpowiedzi z linkiem"""
    id: int
    long_url: str
    short_code: str
    custom_alias: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    clicks: int
    short_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class LinkUpdate(BaseModel):
    """Schemat do aktualizacji linku"""
    long_url: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class LinkList(BaseModel):
    """Schemat listy linków"""
    total: int
    links: list[LinkResponse]


class LinkListResponse(BaseModel):
    """Schemat odpowiedzi z listą linków z paginacją"""
    total: int
    page: int
    page_size: int
    items: list[LinkResponse]
