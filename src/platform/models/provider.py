"""Provider model."""

from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base

class Provider(Base):
    """A skilled individual offering services."""
    
    __tablename__ = "providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Identity
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    verified = Column(Boolean, default=False)
    
    # Profile
    business_name = Column(String(255))  # Optional business/brand name
    bio = Column(Text)
    profile_photo_url = Column(String(500))
    years_experience = Column(Integer)
    
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
    
    # Sprint 10: Performance Stats
    jobs_completed = Column(Integer, default=0)
    response_rate = Column(Float, default=0.0)  # Percentage (0-100)
    average_response_time_hours = Column(Float)
    
    # Sprint 9: Offer Templates
    offer_templates = Column(JSON, default=list)
    
    # Status
    status = Column(String(50), default="active")

class ProviderLeadView(Base):
    """Tracks when a provider has viewed a specific lead."""
    __tablename__ = "provider_lead_views"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), index=True)
    request_id = Column(UUID(as_uuid=True), index=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

class ProviderEnrollment(Base):
    """Temporary storage for a provider's enrollment process."""
    __tablename__ = "provider_enrollments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    status = Column(String(50), default="draft") # draft, pending, verified, rejected
    
    # Store all conversational gathering in a JSON block
    data = Column(JSON, default=dict)
    
    # Links to a permanent provider record once activated
    provider_id = Column(UUID(as_uuid=True), nullable=True)

class ProviderPortfolioPhoto(Base):
    """Portfolio photos for a provider."""
    __tablename__ = "provider_portfolio_photos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    photo_url = Column(String(500), nullable=False)
    caption = Column(Text)
    display_order = Column(Integer, default=0)  # For manual ordering
