from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.platform.database import get_db
from src.platform.models.booking import Booking
from src.platform.schemas.booking import BookingResponse, BookingUpdate

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: UUID, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}/complete", response_model=BookingResponse)
def complete_booking(booking_id: UUID, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    booking.status = "completed"
    
    # Store completion details
    booking.completion = {
        "completed_at": datetime.utcnow().isoformat(),
        "final_price": booking.price
    }
    
    db.commit()
    db.refresh(booking)
    return booking

@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(booking_id: UUID, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    booking.status = "cancelled"
    booking.cancellation = {
         "cancelled_at": datetime.utcnow().isoformat(),
         "cancelled_by": "unknown" # Need auth context to know who
    }
    
    db.commit()
    db.refresh(booking)
    return booking
