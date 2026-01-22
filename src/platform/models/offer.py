"""Offer model."""

from sqlalchemy import Column, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Offer(Base):
    """A provider's offer in response to a request."""
    
    __tablename__ = "offers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # References
    request_id = Column(UUID(as_uuid=True), ForeignKey("service_requests.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    
    # Offer details
    service_name = Column(String(255))
    available_slots = Column(JSON)
    price = Column(Float)
    currency = Column(String(10), default="USD")
    price_notes = Column(Text)
    
    # Provider snapshot
    provider_snapshot = Column(JSON)
    
    # Message
    message = Column(Text)
    
    # Status
    status = Column(String(50), default="pending")
