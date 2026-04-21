from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Konfiguracja aplikacji Link Management"""
    
    # Database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/url_shortener"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Application
    app_name: str = "Link Management Service"
    api_version: str = "v1"
    debug: bool = True
    
    # Short code settings
    short_code_length: int = 6
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
