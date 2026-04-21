import string
import random
from nanoid import generate
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from src.models.link import Link
from src.schemas.link import LinkCreate, LinkUpdate
from src.core.config import settings
from src.services.url_validator import URLValidator
import logging

logger = logging.getLogger(__name__)


class LinkService:
    """Serwis do zarządzania linkami"""
    
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        """
        Generuje unikalny krótki kod używając nanoid.
        Nanoid jest bezpieczniejszą i bardziej efektywną alternatywą dla UUID.
        """
        # Alfabet bez mylących znaków (0, O, I, l)
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        return generate(alphabet, length)
    
    @staticmethod
    def create_link(db: Session, link_data: LinkCreate) -> Link:
        """Tworzy nowy skrócony link"""
        
        # KROK 1: Walidacja URL
        normalized_url = URLValidator.normalize_url(str(link_data.long_url))
        is_valid, error_msg = URLValidator.validate_url(normalized_url)
        
        if not is_valid:
            raise ValueError(f"Niepoprawny URL: {error_msg}")
        
        # KROK 2: Sprawdzenie duplikatów (zwróć istniejący link)
        existing = db.query(Link).filter(
            Link.long_url == normalized_url
        ).first()
        
        if existing and existing.is_active:
            logger.info(f"Zwracam istniejący link dla URL: {normalized_url}")
            # Sprawdź czy nie wygasł
            if LinkService.is_link_valid(existing):
                return existing
            else:
                # Jeśli wygasł, utwórz nowy
                logger.info(f"Istniejący link wygasł, tworzę nowy")
        
        # KROK 3: Użyj własnego aliasu lub wygeneruj kod
        if link_data.custom_alias:
            # Walidacja aliasu
            if not link_data.custom_alias.replace('-', '').replace('_', '').isalnum():
                raise ValueError(
                    "Alias może zawierać tylko litery, cyfry, myślniki i podkreślenia"
                )
            
            # Sprawdź czy alias jest wolny
            if db.query(Link).filter(Link.short_code == link_data.custom_alias).first():
                raise ValueError(f"Alias '{link_data.custom_alias}' jest już zajęty")
            short_code = link_data.custom_alias
        else:
            # Generuj unikalny kod
            max_attempts = 10
            for _ in range(max_attempts):
                short_code = LinkService.generate_short_code(settings.short_code_length)
                if not db.query(Link).filter(Link.short_code == short_code).first():
                    break
            else:
                raise RuntimeError("Nie udało się wygenerować unikalnego kodu")
        
        # KROK 4: Utwórz nowy link
        db_link = Link(
            long_url=normalized_url,
            short_code=short_code,
            custom_alias=link_data.custom_alias,
            expires_at=link_data.expires_at,
            is_active=True,
            clicks=0
        )
        
        logger.info(f"Utworzono nowy link: {short_code} -> {normalized_url}")
        
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        
        return db_link
    
    @staticmethod
    def get_link_by_code(db: Session, short_code: str) -> Optional[Link]:
        """Pobiera link po kodzie"""
        return db.query(Link).filter(Link.short_code == short_code).first()
    
    @staticmethod
    def get_link_by_id(db: Session, link_id: int) -> Optional[Link]:
        """Pobiera link po ID"""
        return db.query(Link).filter(Link.id == link_id).first()
    
    @staticmethod
    def get_all_links(db: Session, skip: int = 0, limit: int = 100) -> List[Link]:
        """Pobiera wszystkie linki z paginacją"""
        return db.query(Link).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_links(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Link]:
        """Pobiera linki z paginacją i filtrowaniem"""
        query = db.query(Link)
        
        if active_only:
            query = query.filter(Link.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_link(db: Session, link_id: int, link_update: LinkUpdate) -> Optional[Link]:
        """Aktualizuje link"""
        db_link = db.query(Link).filter(Link.id == link_id).first()
        if not db_link:
            return None
        
        update_data = link_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_link, field, value)
        
        db.commit()
        db.refresh(db_link)
        return db_link
    
    @staticmethod
    def delete_link(db: Session, link_id: int) -> bool:
        """Usuwa link (soft delete - ustawia is_active na False)"""
        db_link = db.query(Link).filter(Link.id == link_id).first()
        if not db_link:
            return False
        
        db_link.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def increment_clicks(db: Session, short_code: str) -> bool:
        """Inkrementuje licznik kliknięć"""
        db_link = db.query(Link).filter(Link.short_code == short_code).first()
        if not db_link:
            return False
        
        db_link.clicks += 1
        db.commit()
        return True
    
    @staticmethod
    def is_link_valid(link: Link) -> bool:
        """Sprawdza czy link jest aktywny i nie wygasł"""
        if not link.is_active:
            return False
        
        if link.expires_at and link.expires_at < datetime.now(link.expires_at.tzinfo):
            return False
        
        return True
