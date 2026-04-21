import string
import random
from nanoid import generate
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from src.models.link import Link
from src.schemas.link import LinkCreate, LinkUpdate
from src.core.config import settings


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
        
        # Sprawdź czy URL już istnieje (opcjonalnie można zwrócić istniejący)
        existing = db.query(Link).filter(Link.long_url == str(link_data.long_url)).first()
        if existing and existing.is_active:
            return existing
        
        # Użyj własnego aliasu lub wygeneruj kod
        if link_data.custom_alias:
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
        
        # Utwórz nowy link
        db_link = Link(
            long_url=str(link_data.long_url),
            short_code=short_code,
            custom_alias=link_data.custom_alias,
            expires_at=link_data.expires_at,
            is_active=True,
            clicks=0
        )
        
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
