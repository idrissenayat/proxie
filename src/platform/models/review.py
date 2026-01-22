"""Review model."""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Review(Base):
    """A consumer review of a provider."""
    
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # References
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    consumer_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Rating
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    
    # Detailed ratings
    ratings_breakdown = Column(JSON)
    
    # Visibility
    visible = Column(Boolean, default=True)
    
    # Provider response
    response = Column(JSON)
