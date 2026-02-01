-- Database Migration: Agent Memory Tables
-- Phase 1 of Agent Architecture v2

-- Enable pgvector if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Consumer Memory Table
CREATE TABLE IF NOT EXISTS consumer_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID NOT NULL REFERENCES consumers(id) ON DELETE CASCADE,
    
    -- Explicit preferences
    preferred_budget_min DECIMAL(10,2),
    preferred_budget_max DECIMAL(10,2),
    preferred_timing VARCHAR(50),
    communication_style VARCHAR(50),
    
    -- Learned preferences (JSON for flexibility)
    learned_preferences JSONB DEFAULT '{}'::jsonb,
    
    -- Interaction stats
    total_bookings INTEGER DEFAULT 0,
    total_requests INTEGER DEFAULT 0,
    avg_rating_given DECIMAL(3,2),
    
    -- Embeddings (using 3072 dimensions for text-embedding-3-large)
    preference_embedding VECTOR(3072),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_consumer_memory_embedding 
ON consumer_memories USING ivfflat(preference_embedding vector_cosine_ops);

-- 2. Provider Memory Table  
CREATE TABLE IF NOT EXISTS provider_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    
    -- Performance metrics
    total_leads_received INTEGER DEFAULT 0,
    total_offers_sent INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,4) DEFAULT 0,
    avg_response_time_hours DECIMAL(6,2),
    
    -- Pricing intelligence
    pricing_history JSONB DEFAULT '[]'::jsonb,
    market_position VARCHAR(50),
    
    -- Schedule patterns
    schedule_patterns JSONB DEFAULT '{}'::jsonb,
    
    -- Feedback analysis
    feedback_themes JSONB DEFAULT '{}'::jsonb,
    
    -- Goals
    weekly_booking_target INTEGER,
    revenue_target DECIMAL(10,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Specialist Knowledge Base Table
CREATE TABLE IF NOT EXISTS specialist_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_type VARCHAR(100) NOT NULL,  -- 'haircut', 'cleaning', etc.
    
    -- Knowledge content
    pricing_rules JSONB NOT NULL,
    quality_indicators JSONB NOT NULL,
    domain_vocabulary JSONB DEFAULT '{}'::jsonb,
    
    -- Learned patterns
    successful_patterns JSONB DEFAULT '[]'::jsonb,
    regional_adjustments JSONB DEFAULT '{}'::jsonb,
    
    -- Versioning
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Agent Interaction Log (for learning)
CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    user_id UUID,
    
    -- Interaction details
    interaction_type VARCHAR(50),  -- 'request', 'offer', 'booking', 'feedback'
    input_summary TEXT,
    output_summary TEXT,
    tools_used JSONB DEFAULT '[]'::jsonb,
    
    -- Outcome tracking
    outcome VARCHAR(50),  -- 'success', 'abandoned', 'error'
    user_satisfaction INTEGER,  -- 1-5 if feedback given
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interactions_user ON agent_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON agent_interactions(agent_type, interaction_type);
