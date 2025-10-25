from sqlalchemy import Column, ForeignKey, DateTime, BigInteger, Integer
from sqlalchemy.sql import func
from app.database import Base


class URLAnalytics(Base):
    __tablename__ = "url_analytics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("url_mappings.id"), nullable=False)
    click_count = Column(BigInteger, nullable=False, default=0)
    start_at = Column(DateTime(timezone=True))
    end_at= Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, onupdate=func.now())