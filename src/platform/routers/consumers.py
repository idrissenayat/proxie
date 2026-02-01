from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.platform.database import get_db
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.models.booking import Booking
from src.platform.models.provider import Provider
from src.platform.models.consumer import Consumer
from src.platform.schemas.consumer import ConsumerRequestsResponse
from src.platform.auth import get_current_user, get_optional_user
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/consumers",
    responses={404: {"description": "Not found"}},
)

class ConsumerProfileUpdate(BaseModel):
    """Request body for updating consumer profile."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_photo_url: Optional[str] = None
    default_location: Optional[Dict[str, Any]] = Field(
        None,
        description="Default location: {city, state, zip, address, lat, lng}"
    )
    notification_preferences: Optional[Dict[str, bool]] = None
    preferences: Optional[Dict[str, Any]] = None

class ConsumerProfileResponse(BaseModel):
    """Response for consumer profile."""
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_photo_url: Optional[str] = None
    default_location: Optional[Dict[str, Any]] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

@router.get("/{consumer_id}/profile", response_model=ConsumerProfileResponse)
async def get_consumer_profile(
    consumer_id: UUID, 
    db: Session = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get consumer profile. Creates a new profile if it doesn't exist."""
    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    
    # Security: Ensure user can only access their own profile (or is admin)
    if user:
        is_admin = user.get("public_metadata", {}).get("role") == "admin"
        if not is_admin:
            # If consumer exists, check its clerk_id
            if consumer and consumer.clerk_id and consumer.clerk_id != user.get("sub"):
                raise HTTPException(status_code=403, detail="Not authorized to access this profile")
            # If consumer exists but has no clerk_id, we might want to link it (guest-to-user)
            # For now, allow it if it has no clerk_id (it's a "shared" or new guest record)
            
            # If consumer doesn't exist, we'll create it below. 
            # In that case, we should ensure the ID being requested doesn't belong to another clerk_id.
            # But we can't know that without checking if THAT UUID is used by someone else as their ID.
            # Usually record ID != clerk ID, so this is fine.
    
    if not consumer:
        # Create a new consumer record
        consumer = Consumer(id=consumer_id)
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
    
    return consumer.to_dict()

@router.put("/{consumer_id}/profile", response_model=ConsumerProfileResponse)
async def update_consumer_profile(
    consumer_id: UUID,
    update: ConsumerProfileUpdate,
    db: Session = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Update consumer profile. Creates profile if it doesn't exist."""
    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    
    # Security: Ensure user can only update their own profile
    if user:
        is_admin = user.get("public_metadata", {}).get("role") == "admin"
        if not is_admin:
            if consumer and consumer.clerk_id and consumer.clerk_id != user.get("sub"):
                raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    if not consumer:
        consumer = Consumer(id=consumer_id)
        db.add(consumer)
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(consumer, field, value)
    
    db.commit()
    db.refresh(consumer)
    
    return consumer.to_dict()

@router.patch("/{consumer_id}/location")
async def update_consumer_location(
    consumer_id: UUID,
    location: Dict[str, Any],
    db: Session = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Quick endpoint to update just the default location."""
    # Security Check
    if user:
        if str(consumer_id) != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this profile")

    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    
    if not consumer:
        consumer = Consumer(id=consumer_id, default_location=location)
        db.add(consumer)
    else:
        consumer.default_location = location
    
    db.commit()
    
    return {"status": "success", "location": location}

@router.get("/me/requests", response_model=ConsumerRequestsResponse)
async def get_my_requests(
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all requests and bookings for the currently authenticated consumer.
    """
    clerk_id = user.get("sub")
    consumer = db.query(Consumer).filter(Consumer.clerk_id == clerk_id).first()
    
    if not consumer:
        # Auto-create profile if authenticated via Clerk but no record exists
        consumer = Consumer(id=uuid4(), clerk_id=clerk_id)
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        
    return get_consumer_requests(consumer.id, db, user)

@router.get("/{consumer_id}/requests", response_model=ConsumerRequestsResponse)
def get_consumer_requests(
    consumer_id: UUID, 
    db: Session = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get all requests and bookings for a consumer, grouped by status.
    """
    # Security Check
    if user:
        clerk_id = user.get("sub")
        # Find if this consumer_id belongs to the current user
        consumer_record = db.query(Consumer).filter(Consumer.id == consumer_id).first()
        
        if consumer_record and consumer_record.clerk_id and consumer_record.clerk_id != clerk_id:
            # Token belongs to someone else
            if user.get("public_metadata", {}).get("role") != "admin":
                raise HTTPException(status_code=403, detail="Not authorized to access these requests")
        
        # Note: If consumer_record has NO clerk_id, we allow it (guest-to-user transition window)

    # 1. Fetch all requests for consumer (optimized with batch loading)
    from sqlalchemy import func
    from src.platform.database.query_utils import optimize_consumer_requests_query
    
    all_requests = db.query(ServiceRequest).filter(ServiceRequest.consumer_id == consumer_id).all()
    
    # Batch load offer counts (fixes N+1)
    request_ids = [r.id for r in all_requests]
    offer_counts = db.query(
        Offer.request_id,
        func.count(Offer.id).label('count')
    ).filter(
        Offer.request_id.in_(request_ids)
    ).group_by(Offer.request_id).all()
    
    offer_count_map = {req_id: count for req_id, count in offer_counts}
    
    # Batch load best offers and providers (fixes N+1)
    from sqlalchemy import and_
    best_offers = db.query(Offer).filter(
        Offer.request_id.in_(request_ids),
        Offer.status == "pending"
    ).order_by(Offer.created_at).all()
    
    # Group by request_id to get first (best) offer per request
    best_offer_map = {}
    provider_ids = set()
    for offer in best_offers:
        if offer.request_id not in best_offer_map:
            best_offer_map[offer.request_id] = offer
            provider_ids.add(offer.provider_id)
    
    # Batch load providers (fixes N+1)
    providers = {p.id: p for p in db.query(Provider).filter(Provider.id.in_(provider_ids)).all()}
    
    open_requests = []
    pending_requests = []
    
    for req in all_requests:
        offer_count = offer_count_map.get(req.id, 0)
        
        summary = {
            "id": req.id,
            "service_type": req.service_type,
            "title": req.raw_input[:50] + "..." if req.raw_input and len(req.raw_input) > 50 else req.raw_input,
            "location": req.location,
            "budget": req.budget,
            "status": req.status,
            "offer_count": offer_count,
            "created_at": req.created_at
        }
        
        # Inclusion logic: show matching, open, and pending requests
        is_open = req.status in ["matching", "open", "pending"]
        
        if is_open and offer_count == 0:
            open_requests.append(summary)
        elif req.status == "offers_received" or (is_open and offer_count > 0):
            # Use pre-loaded best offer
            best_offer_db = best_offer_map.get(req.id)
            if best_offer_db:
                provider = providers.get(best_offer_db.provider_id)
                summary["best_offer"] = {
                    "price": best_offer_db.price,
                    "provider_name": provider.name if provider else "Unknown",
                    "provider_rating": provider.rating if provider else 0.0
                }
            pending_requests.append(summary)
        elif req.status == "booked":
            # These will show up in bookings section usually, but we keep them in all_requests for completeness
            pass

    # 2. Fetch bookings (optimized with batch loading)
    all_bookings = db.query(Booking).filter(Booking.consumer_id == consumer_id).all()
    
    # Batch load providers and reviews (fixes N+1)
    booking_provider_ids = {b.provider_id for b in all_bookings}
    booking_ids = [b.id for b in all_bookings]
    
    booking_providers = {p.id: p for p in db.query(Provider).filter(Provider.id.in_(booking_provider_ids)).all()}
    
    from src.platform.models.review import Review
    reviews = {r.booking_id: r for r in db.query(Review).filter(Review.booking_id.in_(booking_ids)).all()}
    
    upcoming = []
    completed = []
    
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    for b in all_bookings:
        # For simplicity, if status is confirmed, it's upcoming.
        # If status is completed, it's completed.
        
        if b.status == "confirmed":
            # Use pre-loaded provider
            provider = booking_providers.get(b.provider_id)
            upcoming.append({
                "booking_id": b.id,
                "request_id": b.request_id,
                "service_type": b.service_name,
                "provider": {
                    "id": b.provider_id,
                    "name": provider.name if provider else "Unknown",
                    "rating": provider.rating if provider else 0.0
                },
                "scheduled_date": b.scheduled_date,
                "scheduled_time": b.scheduled_start.strftime("%H:%M"),
                "location": b.location,
                "status": b.status
            })
        elif b.status == "completed":
            provider = booking_providers.get(b.provider_id)
            # Use pre-loaded review
            review = reviews.get(b.id)
            
            completed.append({
                "booking_id": b.id,
                "request_id": b.request_id,
                "service_type": b.service_name,
                "provider": {
                    "id": b.provider_id,
                    "name": provider.name if provider else "Unknown"
                },
                "completed_at": b.updated_at, # Using updated_at as proxy for completion time
                "has_review": review is not None,
                "review_rating": review.rating if review else None
            })

    return {
        "consumer_id": consumer_id,
        "requests": {
            "open": open_requests,
            "pending": pending_requests,
            "upcoming": upcoming,
            "completed": completed
        },
        "counts": {
            "open": len(open_requests),
            "pending": len(pending_requests),
            "upcoming": len(upcoming),
            "completed": len(completed)
        }
    }
