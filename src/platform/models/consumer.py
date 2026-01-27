"""Consumer model for service requesters."""

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Consumer(Base):
    """A person seeking services on the platform."""
    
    __tablename__ = "consumers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Identity
    name = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    
    # Profile settings
    profile_photo_url = Column(String(500))
    
    # Default location (so we don't have to ask every time)
    default_location = Column(JSON)  # {city, state, zip, address, lat, lng}
    
    # Communication preferences
    notification_preferences = Column(JSON, default=dict)  # {email: true, sms: true, push: true}
    
    # Previous service preferences (for personalization)
    preferences = Column(JSON, default=dict)  # {preferred_times, budget_range, etc.}
    
    # Stats
    requests_count = Column(String, default="0")
    bookings_count = Column(String, default="0")
    
    def __repr__(self):
        return f"<Consumer {self.name or self.id}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "profile_photo_url": self.profile_photo_url,
            "default_location": self.default_location,
            "notification_preferences": self.notification_preferences,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
