"""Service Request model."""

from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class ServiceRequest(Base):
    """A consumer's service request."""
    
    __tablename__ = "service_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Consumer
    consumer_id = Column(UUID(as_uuid=True))
    consumer_agent_id = Column(String(255))
    
    # Original input
    raw_input = Column(Text)
    
    # Parsed request
    service_category = Column(String(100))
    service_type = Column(String(100))
    requirements = Column(JSON)
    location = Column(JSON)
    timing = Column(JSON)
    budget = Column(JSON)
    
    # Status
    status = Column(String(50), default="pending")
    status_history = Column(JSON, default=list)  # Sprint 10: Timeline tracking
    
    # Results
    matched_providers = Column(JSON, default=list)
    selected_offer_id = Column(UUID(as_uuid=True))
    
    # Sprint 8: Media support
    media = Column(JSON, default=list)
