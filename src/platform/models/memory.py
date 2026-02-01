"""Agent Memory Models."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from src.platform.database import Base

class ConsumerMemory(Base):
    """Persistent memory for a Personal Consumer Agent."""
    __tablename__ = "consumer_memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consumer_id = Column(UUID(as_uuid=True), ForeignKey("consumers.id", ondelete="CASCADE"), nullable=False)
    
    # Explicit preferences
    preferred_budget_min = Column(DECIMAL(10, 2))
    preferred_budget_max = Column(DECIMAL(10, 2))
    preferred_timing = Column(String(50))
    communication_style = Column(String(50))
    
    # Learned preferences (JSON for flexibility)
    learned_preferences = Column(JSONB, server_default='{}')
    
    # Interaction stats
    total_bookings = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    avg_rating_given = Column(DECIMAL(3, 2))
    
    # Embeddings (using 3072 dimensions for text-embedding-3-large)
    preference_embedding = Column(Vector(3072), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProviderMemory(Base):
    """Persistent memory for a Personal Provider Agent."""
    __tablename__ = "provider_memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    
    # Performance metrics
    total_leads_received = Column(Integer, default=0)
    total_offers_sent = Column(Integer, default=0)
    conversion_rate = Column(DECIMAL(5, 2), default=0)
    avg_response_time_hours = Column(DECIMAL(6, 2))
    
    # Pricing intelligence
    pricing_history = Column(JSONB, server_default='[]')
    market_position = Column(String(50))
    
    # Schedule patterns
    schedule_patterns = Column(JSONB, server_default='{}')
    
    # Feedback analysis
    feedback_themes = Column(JSONB, server_default='{}')
    
    # Goals
    weekly_booking_target = Column(Integer)
    revenue_target = Column(DECIMAL(10, 2))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SpecialistKnowledge(Base):
    """Knowledge base for non-conversational Specialist agents."""
    __tablename__ = "specialist_knowledge"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    specialist_type = Column(String(100), nullable=False)
    
    # Knowledge content
    pricing_rules = Column(JSONB, nullable=False)
    quality_indicators = Column(JSONB, nullable=False)
    domain_vocabulary = Column(JSONB, server_default='{}')
    
    # Learned patterns
    successful_patterns = Column(JSONB, server_default='[]')
    regional_adjustments = Column(JSONB, server_default='{}')
    
    # Versioning
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AgentInteraction(Base):
    """Interaction logs for agent optimization and learning."""
    __tablename__ = "agent_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    agent_type = Column(String(50), nullable=False)
    user_id = Column(UUID(as_uuid=True))
    
    # Interaction details
    interaction_type = Column(String(50))  # 'request', 'offer', 'booking', 'feedback'
    input_summary = Column(Text)
    output_summary = Column(Text)
    tools_used = Column(JSONB, server_default='[]')
    
    # Outcome tracking
    outcome = Column(String(50))  # 'success', 'abandoned', 'error'
    user_satisfaction = Column(Integer)  # 1-5 if feedback given
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
