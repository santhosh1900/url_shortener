from sqlalchemy import Column, String, Text, DateTime, BigInteger, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class URLMapping(Base):
    __tablename__ = "url_mappings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    short_code = Column(String(64), unique=True, nullable=False)
    original_url = Column(Text, unique=True, nullable=False)
    click_count = Column(BigInteger, nullable=False, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())