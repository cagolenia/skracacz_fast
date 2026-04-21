from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Tworzenie silnika bazy danych
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug
)

# Sesja bazy danych
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Bazowa klasa dla modeli
Base = declarative_base()


def get_db():
    """Dependency do uzyskania sesji bazy danych"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicjalizacja bazy danych - tworzenie tabel"""
    # Import modeli aby SQLAlchemy je zobaczył
    import src.models.link  # noqa: F401
    Base.metadata.create_all(bind=engine)
