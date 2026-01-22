"""Service model."""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Service(Base):
    """A service offered by a provider."""
    
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Provider reference
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    
    # Service details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer)
    
    # Pricing
    price_min = Column(Float)
    price_max = Column(Float)
    currency = Column(String(10), default="USD")
