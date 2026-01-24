from datetime import datetime
from typing import Optional, Dict
from uuid import UUID
from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    booking_id: UUID
    provider_id: UUID
    consumer_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    ratings_breakdown: Optional[Dict[str, int]] = None

class ReviewResponse(ReviewCreate):
    id: UUID
    created_at: datetime
    visible: bool = True
    
    class Config:
        from_attributes = True
