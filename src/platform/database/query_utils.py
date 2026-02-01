"""
Query optimization utilities for SQLAlchemy.

Provides helpers for eager loading, pagination, and query optimization.
"""

from sqlalchemy.orm import joinedload, selectinload, subqueryload
from sqlalchemy import func
from typing import List, TypeVar, Optional, Tuple
from src.platform.models.provider import Provider, ProviderPortfolioPhoto
from src.platform.models.service import Service
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.models.booking import Booking
from src.platform.models.review import Review
from src.platform.models.consumer import Consumer
from src.platform.models.provider import ProviderLeadView

T = TypeVar('T')


def eager_load_provider(db_query, include_services: bool = True, include_photos: bool = True):
    """
    Add eager loading options for Provider relationships.
    
    Usage:
        query = db.query(Provider).filter(...)
        query = eager_load_provider(query)
        providers = query.all()
    """
    if include_services:
        db_query = db_query.options(selectinload(Provider.services))
    if include_photos:
        db_query = db_query.options(selectinload(Provider.portfolio_photos))
    return db_query


def eager_load_request(db_query, include_offers: bool = True, include_consumer: bool = False):
    """
    Add eager loading options for ServiceRequest relationships.
    
    Usage:
        query = db.query(ServiceRequest).filter(...)
        query = eager_load_request(query)
        requests = query.all()
    """
    if include_offers:
        db_query = db_query.options(selectinload(ServiceRequest.offers))
    if include_consumer:
        db_query = db_query.options(joinedload(ServiceRequest.consumer))
    return db_query


def eager_load_booking(db_query, include_provider: bool = True, include_request: bool = True, include_review: bool = True):
    """
    Add eager loading options for Booking relationships.
    
    Usage:
        query = db.query(Booking).filter(...)
        query = eager_load_booking(query)
        bookings = query.all()
    """
    if include_provider:
        db_query = db_query.options(joinedload(Booking.provider))
    if include_request:
        db_query = db_query.options(joinedload(Booking.request))
    if include_review:
        db_query = db_query.options(joinedload(Booking.review))
    return db_query


def eager_load_offer(db_query, include_provider: bool = True, include_request: bool = True):
    """
    Add eager loading options for Offer relationships.
    
    Usage:
        query = db.query(Offer).filter(...)
        query = eager_load_offer(query)
        offers = query.all()
    """
    if include_provider:
        db_query = db_query.options(joinedload(Offer.provider))
    if include_request:
        db_query = db_query.options(joinedload(Offer.request))
    return db_query


def paginate_query(
    query,
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100
) -> Tuple[List, int]:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum items per page
    
    Returns:
        Tuple of (items, total_count)
    """
    # Clamp per_page
    per_page = min(per_page, max_per_page)
    per_page = max(1, per_page)
    
    # Get total count
    total = query.count()
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get paginated results
    items = query.offset(offset).limit(per_page).all()
    
    return items, total


def optimize_list_requests_query(
    db_query,
    include_viewed_status: bool = False,
    provider_id: Optional[str] = None
):
    """
    Optimize the list_requests query with eager loading and batch operations.
    
    This fixes the N+1 query problem in list_requests.
    """
    # Eager load offers
    db_query = eager_load_request(db_query, include_offers=True)
    
    # If we need viewed status, we'll batch load it
    if include_viewed_status and provider_id:
        # This will be handled separately to avoid N+1
        pass
    
    return db_query


def batch_load_viewed_status(
    db_session,
    request_ids: List,
    provider_id: str
) -> set:
    """
    Batch load viewed status for multiple requests.
    
    This replaces the N+1 query pattern.
    """
    viewed = db_session.query(ProviderLeadView.request_id).filter(
        ProviderLeadView.provider_id == provider_id,
        ProviderLeadView.request_id.in_(request_ids)
    ).all()
    
    return {v[0] for v in viewed}


def optimize_consumer_requests_query(db_query):
    """
    Optimize query for consumer requests with all related data.
    """
    # Eager load offers and their providers
    db_query = db_query.options(
        selectinload(ServiceRequest.offers).joinedload(Offer.provider)
    )
    return db_query


def optimize_consumer_bookings_query(db_query):
    """
    Optimize query for consumer bookings with all related data.
    """
    # Eager load provider, request, and review
    db_query = db_query.options(
        joinedload(Booking.provider),
        joinedload(Booking.request),
        joinedload(Booking.review)
    )
    return db_query
