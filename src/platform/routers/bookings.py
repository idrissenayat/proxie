from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.platform.database import get_db
from src.platform.models.booking import Booking
from src.platform.schemas.booking import BookingResponse, BookingUpdate
from src.platform.auth import get_current_user, require_ownership
from typing import Dict, Any

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Security: Ensure user owns this booking (consumer or provider)
    require_ownership("booking", booking_id, user, db)
    
    return booking

@router.put("/{booking_id}/complete", response_model=BookingResponse)
def complete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Security: Ensure user owns this booking (provider can complete)
    require_ownership("booking", booking_id, user, db)
        
    booking.status = "completed"
    
    # Store completion details
    booking.completion = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "final_price": booking.price
    }
    
    db.commit()
    db.refresh(booking)
    return booking

@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Security: Ensure user owns this booking (consumer or provider can cancel)
    require_ownership("booking", booking_id, user, db)
        
    booking.status = "cancelled"
    booking.cancellation = {
         "cancelled_at": datetime.now(timezone.utc).isoformat(),
         "cancelled_by": user.get("sub", "unknown")
    }
    
    db.commit()
    db.refresh(booking)
    return booking
