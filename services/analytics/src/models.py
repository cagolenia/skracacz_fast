from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from src.database import Base


class LinkVisit(Base):
    """Model dla statystyk odwiedzin linków"""
    
    __tablename__ = "link_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 może mieć do 45 znaków
    user_agent = Column(String(500), nullable=True)
    referer = Column(String(500), nullable=True)
    
    # Opcjonalne pola do dalszej analizy
    country = Column(String(2), nullable=True)  # Kod kraju ISO
    device_type = Column(String(20), nullable=True)  # mobile, desktop, tablet, bot
    
    # Indeksy dla wydajności
    __table_args__ = (
        Index('idx_short_code_timestamp', 'short_code', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<LinkVisit(short_code='{self.short_code}', timestamp='{self.timestamp}')>"
