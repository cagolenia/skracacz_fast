from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Konfiguracja aplikacji Redirection Service"""
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 3600  # Cache TTL w sekundach (1 godzina)
    
    # Link Management Service
    link_management_url: str = "http://localhost:8001"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_queue: str = "link_visits"
    
    # Application
    app_name: str = "Redirection Service"
    api_version: str = "v1"
    debug: bool = True
    
    # Performance
    request_timeout: int = 5  # Timeout dla zapytań HTTP w sekundach
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
