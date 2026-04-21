from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Konfiguracja aplikacji Analytics Service"""
    
    # Database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/url_shortener"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_queue: str = "link_visits"
    
    # Application
    app_name: str = "Analytics Service"
    api_version: str = "v1"
    debug: bool = True
    
    # Worker settings
    worker_prefetch_count: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
