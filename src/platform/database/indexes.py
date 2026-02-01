"""
Database indexes for query optimization.

This module defines indexes that should be created for optimal query performance.
"""

# Index definitions for Alembic migrations
INDEXES = [
    # Providers
    "CREATE INDEX IF NOT EXISTS idx_providers_clerk_id ON providers(clerk_id)",
    "CREATE INDEX IF NOT EXISTS idx_providers_status ON providers(status)",
    "CREATE INDEX IF NOT EXISTS idx_providers_email ON providers(email)",
    "CREATE INDEX IF NOT EXISTS idx_providers_created_at ON providers(created_at DESC)",
    
    # Consumers
    "CREATE INDEX IF NOT EXISTS idx_consumers_clerk_id ON consumers(clerk_id)",
    "CREATE INDEX IF NOT EXISTS idx_consumers_email ON consumers(email)",
    
    # Service Requests
    "CREATE INDEX IF NOT EXISTS idx_requests_consumer_id ON service_requests(consumer_id)",
    "CREATE INDEX IF NOT EXISTS idx_requests_status ON service_requests(status)",
    "CREATE INDEX IF NOT EXISTS idx_requests_created_at ON service_requests(created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_requests_service_category ON service_requests(service_category)",
    "CREATE INDEX IF NOT EXISTS idx_requests_selected_offer_id ON service_requests(selected_offer_id)",
    
    # Offers
    "CREATE INDEX IF NOT EXISTS idx_offers_provider_id ON offers(provider_id)",
    "CREATE INDEX IF NOT EXISTS idx_offers_request_id ON offers(request_id)",
    "CREATE INDEX IF NOT EXISTS idx_offers_status ON offers(status)",
    "CREATE INDEX IF NOT EXISTS idx_offers_created_at ON offers(created_at DESC)",
    
    # Bookings
    "CREATE INDEX IF NOT EXISTS idx_bookings_consumer_id ON bookings(consumer_id)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_provider_id ON bookings(provider_id)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_request_id ON bookings(request_id)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at DESC)",
    
    # Reviews
    "CREATE INDEX IF NOT EXISTS idx_reviews_provider_id ON reviews(provider_id)",
    "CREATE INDEX IF NOT EXISTS idx_reviews_booking_id ON reviews(booking_id)",
    "CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC)",
    
    # Services
    "CREATE INDEX IF NOT EXISTS idx_services_provider_id ON services(provider_id)",
    "CREATE INDEX IF NOT EXISTS idx_services_category ON services(category)",
    
    # Provider Lead Views
    "CREATE INDEX IF NOT EXISTS idx_lead_views_provider_request ON provider_lead_views(provider_id, request_id)",
    "CREATE INDEX IF NOT EXISTS idx_lead_views_request_id ON provider_lead_views(request_id)",
    
    # Provider Portfolio Photos
    "CREATE INDEX IF NOT EXISTS idx_portfolio_photos_provider_id ON provider_portfolio_photos(provider_id)",
    "CREATE INDEX IF NOT EXISTS idx_portfolio_photos_display_order ON provider_portfolio_photos(provider_id, display_order)",
    
    # Composite indexes for common query patterns
    "CREATE INDEX IF NOT EXISTS idx_requests_consumer_status ON service_requests(consumer_id, status)",
    "CREATE INDEX IF NOT EXISTS idx_offers_request_status ON offers(request_id, status)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_consumer_status ON bookings(consumer_id, status)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_provider_status ON bookings(provider_id, status)",
]

# GIN indexes for JSONB columns (PostgreSQL specific)
GIN_INDEXES = [
    # For JSONB queries on location, requirements, etc.
    "CREATE INDEX IF NOT EXISTS idx_requests_location_gin ON service_requests USING GIN(location)",
    "CREATE INDEX IF NOT EXISTS idx_requests_requirements_gin ON service_requests USING GIN(requirements)",
    "CREATE INDEX IF NOT EXISTS idx_providers_location_gin ON providers USING GIN(location)",
    "CREATE INDEX IF NOT EXISTS idx_providers_specializations_gin ON providers USING GIN(specializations)",
]

# Vector indexes for embeddings (pgvector)
VECTOR_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_providers_embedding ON providers USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)",
]


def create_all_indexes(db_session):
    """
    Create all indexes defined above.
    
    This should be called during database initialization or migrations.
    """
    from sqlalchemy import text
    
    for index_sql in INDEXES:
        try:
            db_session.execute(text(index_sql))
            db_session.commit()
        except Exception as e:
            print(f"Error creating index: {e}")
            db_session.rollback()
    
    # GIN indexes (PostgreSQL only)
    try:
        for index_sql in GIN_INDEXES:
            db_session.execute(text(index_sql))
            db_session.commit()
    except Exception as e:
        print(f"Error creating GIN indexes (may not be PostgreSQL): {e}")
        db_session.rollback()
    
    # Vector indexes (pgvector only)
    try:
        for index_sql in VECTOR_INDEXES:
            db_session.execute(text(index_sql))
            db_session.commit()
    except Exception as e:
        print(f"Error creating vector indexes (pgvector may not be installed): {e}")
        db_session.rollback()
