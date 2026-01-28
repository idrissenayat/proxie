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
from src.platform.auth import get_current_user
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
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get consumer profile. Creates a new profile if it doesn't exist."""
    # Security: Ensure user can only access their own profile (or is admin)
    if str(consumer_id) != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this profile")

    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    
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
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Update consumer profile. Creates profile if it doesn't exist."""
    # Security: Ensure user can only update their own profile
    if str(consumer_id) != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")

    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    
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
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Quick endpoint to update just the default location."""
    # Security Check
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

@router.get("/{consumer_id}/requests", response_model=ConsumerRequestsResponse)
def get_consumer_requests(
    consumer_id: UUID, 
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all requests and bookings for a consumer, grouped by status.
    """
    # Security Check
    if str(consumer_id) != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access these requests")

    # 1. Fetch all requests for consumer
    all_requests = db.query(ServiceRequest).filter(ServiceRequest.consumer_id == consumer_id).all()
    
    open_requests = []
    pending_requests = []
    
    for req in all_requests:
        # Count offers for this request
        offer_count = db.query(Offer).filter(Offer.request_id == req.id).count()
        
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
        
        if req.status == "matching" and offer_count == 0:
            open_requests.append(summary)
        elif req.status == "offers_received" or (req.status == "matching" and offer_count > 0):
            # Fetch "best" offer preview (e.g., highest rated provider)
            best_offer_db = db.query(Offer).filter(Offer.request_id == req.id, Offer.status == "pending").first()
            if best_offer_db:
                # Get provider details
                provider = db.query(Provider).filter(Provider.id == best_offer_db.provider_id).first()
                summary["best_offer"] = {
                    "price": best_offer_db.price,
                    "provider_name": provider.name if provider else "Unknown",
                    "provider_rating": provider.rating if provider else 0.0
                }
            pending_requests.append(summary)

    # 2. Fetch bookings
    all_bookings = db.query(Booking).filter(Booking.consumer_id == consumer_id).all()
    
    upcoming = []
    completed = []
    
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    for b in all_bookings:
        # For simplicity, if status is confirmed, it's upcoming.
        # If status is completed, it's completed.
        
        if b.status == "confirmed":
            # Get provider
            provider = db.query(Provider).filter(Provider.id == b.provider_id).first()
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
            provider = db.query(Provider).filter(Provider.id == b.provider_id).first()
            # Check if there is a review (Assume no Review model implementation yet, or check a Review table)
            # For now, we'll check if a review exists in a hypothetical reviews table
            from src.platform.models.review import Review
            review = db.query(Review).filter(Review.booking_id == b.id).first()
            
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
