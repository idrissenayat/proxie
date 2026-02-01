"""Add database indexes for query optimization

Revision ID: 001_add_indexes
Revises: 
Create Date: 2026-01-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_indexes'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for query optimization."""
    
    # Providers
    op.create_index('idx_providers_clerk_id', 'providers', ['clerk_id'], unique=False, if_not_exists=True)
    op.create_index('idx_providers_status', 'providers', ['status'], unique=False, if_not_exists=True)
    op.create_index('idx_providers_email', 'providers', ['email'], unique=False, if_not_exists=True)
    op.create_index('idx_providers_created_at', 'providers', [sa.text('created_at DESC')], unique=False, if_not_exists=True)
    
    # Consumers
    op.create_index('idx_consumers_clerk_id', 'consumers', ['clerk_id'], unique=False, if_not_exists=True)
    op.create_index('idx_consumers_email', 'consumers', ['email'], unique=False, if_not_exists=True)
    
    # Service Requests
    op.create_index('idx_requests_consumer_id', 'service_requests', ['consumer_id'], unique=False, if_not_exists=True)
    op.create_index('idx_requests_status', 'service_requests', ['status'], unique=False, if_not_exists=True)
    op.create_index('idx_requests_created_at', 'service_requests', [sa.text('created_at DESC')], unique=False, if_not_exists=True)
    op.create_index('idx_requests_service_category', 'service_requests', ['service_category'], unique=False, if_not_exists=True)
    op.create_index('idx_requests_selected_offer_id', 'service_requests', ['selected_offer_id'], unique=False, if_not_exists=True)
    
    # Offers
    op.create_index('idx_offers_provider_id', 'offers', ['provider_id'], unique=False, if_not_exists=True)
    op.create_index('idx_offers_request_id', 'offers', ['request_id'], unique=False, if_not_exists=True)
    op.create_index('idx_offers_status', 'offers', ['status'], unique=False, if_not_exists=True)
    op.create_index('idx_offers_created_at', 'offers', [sa.text('created_at DESC')], unique=False, if_not_exists=True)
    
    # Bookings
    op.create_index('idx_bookings_consumer_id', 'bookings', ['consumer_id'], unique=False, if_not_exists=True)
    op.create_index('idx_bookings_provider_id', 'bookings', ['provider_id'], unique=False, if_not_exists=True)
    op.create_index('idx_bookings_request_id', 'bookings', ['request_id'], unique=False, if_not_exists=True)
    op.create_index('idx_bookings_status', 'bookings', ['status'], unique=False, if_not_exists=True)
    op.create_index('idx_bookings_created_at', 'bookings', [sa.text('created_at DESC')], unique=False, if_not_exists=True)
    
    # Reviews
    op.create_index('idx_reviews_provider_id', 'reviews', ['provider_id'], unique=False, if_not_exists=True)
    op.create_index('idx_reviews_booking_id', 'reviews', ['booking_id'], unique=False, if_not_exists=True)
    op.create_index('idx_reviews_created_at', 'reviews', [sa.text('created_at DESC')], unique=False, if_not_exists=True)
    
    # Services
    op.create_index('idx_services_provider_id', 'services', ['provider_id'], unique=False, if_not_exists=True)
    op.create_index('idx_services_category', 'services', ['category'], unique=False, if_not_exists=True)
    
    # Provider Lead Views
    op.create_index('idx_lead_views_provider_request', 'provider_lead_views', ['provider_id', 'request_id'], unique=False, if_not_exists=True)
    op.create_index('idx_lead_views_request_id', 'provider_lead_views', ['request_id'], unique=False, if_not_exists=True)
    
    # Provider Portfolio Photos
    op.create_index('idx_portfolio_photos_provider_id', 'provider_portfolio_photos', ['provider_id'], unique=False, if_not_exists=True)
    op.create_index('idx_portfolio_photos_display_order', 'provider_portfolio_photos', ['provider_id', 'display_order'], unique=False, if_not_exists=True)
    
    # Composite indexes
    op.create_index('idx_requests_consumer_status', 'service_requests', ['consumer_id', 'status'], unique=False, if_not_exists=True)
    op.create_index('idx_offers_request_status', 'offers', ['request_id', 'status'], unique=False, if_not_exists=True)
    op.create_index('idx_bookings_consumer_status', 'bookings', ['consumer_id', 'status'], unique=False, if_not_exists=True)
    op.create_index('idx_bookings_provider_status', 'bookings', ['provider_id', 'status'], unique=False, if_not_exists=True)


def downgrade() -> None:
    """Remove indexes."""
    
    # Composite indexes
    op.drop_index('idx_bookings_provider_status', table_name='bookings', if_exists=True)
    op.drop_index('idx_bookings_consumer_status', table_name='bookings', if_exists=True)
    op.drop_index('idx_offers_request_status', table_name='offers', if_exists=True)
    op.drop_index('idx_requests_consumer_status', table_name='service_requests', if_exists=True)
    
    # Provider Portfolio Photos
    op.drop_index('idx_portfolio_photos_display_order', table_name='provider_portfolio_photos', if_exists=True)
    op.drop_index('idx_portfolio_photos_provider_id', table_name='provider_portfolio_photos', if_exists=True)
    
    # Provider Lead Views
    op.drop_index('idx_lead_views_request_id', table_name='provider_lead_views', if_exists=True)
    op.drop_index('idx_lead_views_provider_request', table_name='provider_lead_views', if_exists=True)
    
    # Services
    op.drop_index('idx_services_category', table_name='services', if_exists=True)
    op.drop_index('idx_services_provider_id', table_name='services', if_exists=True)
    
    # Reviews
    op.drop_index('idx_reviews_created_at', table_name='reviews', if_exists=True)
    op.drop_index('idx_reviews_booking_id', table_name='reviews', if_exists=True)
    op.drop_index('idx_reviews_provider_id', table_name='reviews', if_exists=True)
    
    # Bookings
    op.drop_index('idx_bookings_created_at', table_name='bookings', if_exists=True)
    op.drop_index('idx_bookings_status', table_name='bookings', if_exists=True)
    op.drop_index('idx_bookings_request_id', table_name='bookings', if_exists=True)
    op.drop_index('idx_bookings_provider_id', table_name='bookings', if_exists=True)
    op.drop_index('idx_bookings_consumer_id', table_name='bookings', if_exists=True)
    
    # Offers
    op.drop_index('idx_offers_created_at', table_name='offers', if_exists=True)
    op.drop_index('idx_offers_status', table_name='offers', if_exists=True)
    op.drop_index('idx_offers_request_id', table_name='offers', if_exists=True)
    op.drop_index('idx_offers_provider_id', table_name='offers', if_exists=True)
    
    # Service Requests
    op.drop_index('idx_requests_selected_offer_id', table_name='service_requests', if_exists=True)
    op.drop_index('idx_requests_service_category', table_name='service_requests', if_exists=True)
    op.drop_index('idx_requests_created_at', table_name='service_requests', if_exists=True)
    op.drop_index('idx_requests_status', table_name='service_requests', if_exists=True)
    op.drop_index('idx_requests_consumer_id', table_name='service_requests', if_exists=True)
    
    # Consumers
    op.drop_index('idx_consumers_email', table_name='consumers', if_exists=True)
    op.drop_index('idx_consumers_clerk_id', table_name='consumers', if_exists=True)
    
    # Providers
    op.drop_index('idx_providers_created_at', table_name='providers', if_exists=True)
    op.drop_index('idx_providers_email', table_name='providers', if_exists=True)
    op.drop_index('idx_providers_status', table_name='providers', if_exists=True)
    op.drop_index('idx_providers_clerk_id', table_name='providers', if_exists=True)
