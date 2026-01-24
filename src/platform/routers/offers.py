from typing import List
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.platform.database import get_db
from src.platform.models.offer import Offer
from src.platform.models.request import ServiceRequest
from src.platform.models.booking import Booking
from src.platform.schemas.offer import OfferCreate, OfferResponse, OfferUpdate
from src.platform.schemas.booking import BookingResponse, BookingLocation

router = APIRouter(
    prefix="/offers",
    tags=["offers"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer: OfferCreate, 
    db: Session = Depends(get_db)
):
    """
    Provider submits an offer in response to a request.
    """
    # Verify request exists
    req = db.query(ServiceRequest).filter(ServiceRequest.id == offer.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Service Request not found")
        
    # Convert slots to dict list for JSON storage
    slots_data = [slot.model_dump(mode='json') for slot in offer.available_slots]
    
    db_offer = Offer(
        request_id=offer.request_id,
        provider_id=offer.provider_id,
        service_id=offer.service_id,
        service_name=offer.service_name,
        available_slots=slots_data,
        price=offer.price,
        currency=offer.currency,
        price_notes=offer.price_notes,
        message=offer.message,
        expires_at=offer.expires_at,
        status="pending"
    )
    
    # Ideally populate provider_snapshot from Provider table here
    # For MVP we might skip or let client provide it? 
    # The schema has provider_snapshot in response but not Create? 
    # Wait, looking at OfferCreate in schemas/offer.py... it does NOT have provider_snapshot.
    # The Schema definition in step 176 has `provider_snapshot` in `OfferResponse` but not `OfferCreate`.
    # So we should probably fetch it from Provider table.
    # For now, we'll leave it empty or implement a quick fetch if needed.
    
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    
    # Update request status to offers_received
    if req.status == "matching":
        req.status = "offers_received"
        db.commit()
        
    return db_offer

@router.put("/{offer_id}/accept", response_model=BookingResponse)
def accept_offer(offer_id: UUID, db: Session = Depends(get_db)):
    """
    Consumer accepts an offer, creating a confirmed booking.
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    if offer.status != "pending":
        raise HTTPException(status_code=400, detail=f"Offer is {offer.status}, cannot accept")
        
    req = db.query(ServiceRequest).filter(ServiceRequest.id == offer.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Associated request not found")
        
    # 1. Update Offer Status
    offer.status = "accepted"
    
    # 2. Update Request Status
    req.status = "booked"
    req.selected_offer_id = offer.id
    
    # 3. Create Booking
    # We need to pick a slot. For MVP, assume the FIRST slot offered is the one booked?
    # Or consumer should specify? The schema doesn't specify slot selection in 'accept'.
    # docs/schemas/booking.md says "Booking confirmed".
    # Let's assume the offer was for a specific slot or the first one is picked.
    if not offer.available_slots:
         raise HTTPException(status_code=400, detail="Offer has no available slots")
    
    # Taking the first slot for simplicity in MVP
    # In real app, consumer would PUT /accept with { "selected_slot": ... }
    slot = offer.available_slots[0] 
    # slot is a dict from JSON
    
    # Construct location (Pull from Request location or Provider? Docs: provider_location, consumer_location)
    # Use dummy for now
    booking_loc = {
        "type": "provider_location",
        "address": "123 Provider St" # This should come from Provider.location
    }
    
    booking = Booking(
        id=uuid4(),
        request_id=req.id,
        offer_id=offer.id,
        provider_id=offer.provider_id,
        consumer_id=req.consumer_id,
        service_id=offer.service_id,
        service_name=offer.service_name,
        scheduled_date=datetime.strptime(slot['date'], "%Y-%m-%d").date(),
        scheduled_start=datetime.strptime(slot['start_time'], "%H:%M").time(),
        scheduled_end=datetime.strptime(slot['end_time'], "%H:%M").time(),
        timezone="UTC", # Default
        location=booking_loc,
        price=offer.price,
        currency=offer.currency,
        status="confirmed"
    )
    
    db.add(booking)
    db.commit()
    
    # Refresh to return
    db.refresh(booking)
    return booking

@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(offer_id: UUID, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer
