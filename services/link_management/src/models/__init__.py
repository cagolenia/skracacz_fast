from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from datetime import datetime
from src.core.database import Base


class Link(Base):
    """Model bazy danych dla skróconych linków"""
    
    __tablename__ = "links"
    
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(Text, nullable=False)
    short_code = Column(String(50), unique=True, index=True, nullable=False)
    custom_alias = Column(String(100), unique=True, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    
    # Opcjonalne pola użytkownika (dla przyszłej funkcjonalności)
    user_id = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Link(id={self.id}, short_code={self.short_code}, long_url={self.long_url[:50]}...)>"
