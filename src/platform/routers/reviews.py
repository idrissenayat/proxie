from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.platform.database import get_db
from src.platform.models.review import Review
from src.platform.models.booking import Booking
from src.platform.schemas.review import ReviewCreate, ReviewResponse
from src.platform.auth import get_current_user
from typing import Dict, Any

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate, 
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Submit a review for a completed booking.
    """
    # Verify booking exists and is completed
    booking = db.query(Booking).filter(Booking.id == review.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed bookings")
        
    db_review = Review(
        booking_id=review.booking_id,
        provider_id=review.provider_id,
        consumer_id=review.consumer_id,
        rating=review.rating,
        comment=review.comment,
        ratings_breakdown=review.ratings_breakdown
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review

@router.get("/provider/{provider_id}", response_model=List[ReviewResponse])
def get_provider_reviews(provider_id: UUID, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.provider_id == provider_id).all()
    return reviews
