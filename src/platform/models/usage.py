"""LLM Usage model to track per-user and per-session costs."""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base

class LLMUsage(Base):
    """Tracks LLM token consumption and estimated cost."""
    
    __tablename__ = "llm_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Identifiers
    user_id = Column(String(255), index=True, nullable=True) # Clerk ID or guest session
    session_id = Column(String(255), index=True, nullable=True)
    
    # Model info
    provider = Column(String(50))
    model = Column(String(100))
    
    # Tokens
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost
    estimated_cost_usd = Column(Float, default=0.0)
    
    # Metadata
    feature = Column(String(100)) # e.g. "chat", "matching", "catalog_generation"
