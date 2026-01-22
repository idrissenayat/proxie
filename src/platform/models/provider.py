"""Provider model."""

from sqlalchemy import Column, String, Boolean, Float, Integer, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Provider(Base):
    """A skilled individual offering services."""
    
    __tablename__ = "providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Identity
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    verified = Column(Boolean, default=False)
    
    # Profile
    bio = Column(Text)
    profile_photo_url = Column(String(500))
    
    # Location (stored as JSON for flexibility)
    location = Column(JSON)
    
    # Specializations
    specializations = Column(JSON, default=list)
    
    # Availability (stored as JSON)
    availability = Column(JSON)
    
    # Settings
    settings = Column(JSON, default=dict)
    
    # Reputation (calculated fields)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    completed_bookings = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="active")
