"""Booking model."""

from sqlalchemy import Column, String, Float, Date, Time, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Booking(Base):
    """A confirmed appointment."""
    
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # References
    request_id = Column(UUID(as_uuid=True), ForeignKey("service_requests.id"))
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id"))
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    consumer_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Service
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    service_name = Column(String(255))
    
    # Schedule
    scheduled_date = Column(Date, nullable=False)
    scheduled_start = Column(Time, nullable=False)
    scheduled_end = Column(Time)
    timezone = Column(String(50))
    
    # Location
    location = Column(JSON)
    
    # Pricing
    price = Column(Float)
    currency = Column(String(10), default="USD")
    
    # Status
    status = Column(String(50), default="confirmed")
    
    # Cancellation details
    cancellation = Column(JSON)
    
    # Completion details
    completion = Column(JSON)
