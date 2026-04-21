"""
Skrypt do inicjalizacji bazy danych.
Tworzy wszystkie tabele zdefiniowane w modelach.
"""
import sys
from pathlib import Path

# Dodaj katalog główny do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import init_db, engine
from src.models.link import Link
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Inicjalizuje bazę danych"""
    logger.info("Inicjalizacja bazy danych...")
    
    try:
        # Sprawdź połączenie
        with engine.connect() as conn:
            logger.info("Połączenie z bazą danych nawiązane pomyślnie")
        
        # Utwórz tabele
        init_db()
        logger.info("Tabele utworzone pomyślnie!")
        
        # Wyświetl informacje o tabelach
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Utworzone tabele: {', '.join(tables)}")
        
    except Exception as e:
        logger.error(f"Błąd podczas inicjalizacji bazy danych: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
