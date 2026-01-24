from datetime import date, datetime
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel

class BookingLocation(BaseModel):
    type: Literal["provider_location", "consumer_location", "other"]
    address: str
    instructions: Optional[str] = None

class BookingCreate(BaseModel):
    request_id: UUID
    offer_id: UUID
    provider_id: UUID
    consumer_id: UUID
    service_id: UUID
    service_name: str
    scheduled_date: date
    scheduled_start: str
    scheduled_end: str
    timezone: str
    location: BookingLocation
    price: float
    currency: str = "USD"

class BookingResponse(BookingCreate):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    
    class Config:
        from_attributes = True

class BookingUpdate(BaseModel):
    status: Optional[str] = None
