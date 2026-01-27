-- Sprint 10: Request Details & Provider Profiles Migration
-- This migration adds new fields to support provider profiles and request details

-- ============================================================================
-- PART 1: Provider Profile Enhancements
-- ============================================================================

-- Add new profile fields to providers table
ALTER TABLE providers 
ADD COLUMN IF NOT EXISTS business_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS years_experience INTEGER,
ADD COLUMN IF NOT EXISTS jobs_completed INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS response_rate FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS average_response_time_hours FLOAT;

-- Create index on provider_id for portfolio lookups
CREATE INDEX IF NOT EXISTS idx_providers_id ON providers(id);

-- ============================================================================
-- PART 2: Provider Portfolio Photos Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS provider_portfolio_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    photo_url VARCHAR(500) NOT NULL,
    caption TEXT,
    display_order INTEGER DEFAULT 0
);

-- Create index for efficient portfolio queries
CREATE INDEX IF NOT EXISTS idx_portfolio_provider_id ON provider_portfolio_photos(provider_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_display_order ON provider_portfolio_photos(provider_id, display_order);

-- ============================================================================
-- PART 3: Service Request Enhancements
-- ============================================================================

-- Add status_history field to service_requests table
ALTER TABLE service_requests 
ADD COLUMN IF NOT EXISTS status_history JSONB DEFAULT '[]'::jsonb;

-- Initialize status_history for existing requests
UPDATE service_requests 
SET status_history = jsonb_build_array(
    jsonb_build_object(
        'status', status,
        'timestamp', created_at,
        'note', 'Initial status'
    )
)
WHERE status_history = '[]'::jsonb OR status_history IS NULL;

-- Create index for status queries
CREATE INDEX IF NOT EXISTS idx_requests_status ON service_requests(status);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify providers table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'providers'
AND column_name IN ('business_name', 'years_experience', 'jobs_completed', 'response_rate', 'average_response_time_hours')
ORDER BY ordinal_position;

-- Verify portfolio table creation
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'provider_portfolio_photos'
ORDER BY ordinal_position;

-- Verify service_requests table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'service_requests'
AND column_name = 'status_history';

-- Count existing records
SELECT 
    (SELECT COUNT(*) FROM providers) as provider_count,
    (SELECT COUNT(*) FROM provider_portfolio_photos) as portfolio_count,
    (SELECT COUNT(*) FROM service_requests) as request_count;
