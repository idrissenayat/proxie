from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, ConfigDict

# --- Sub-models ---

class TimeSlot(BaseModel):
    date: date
    start_time: str
    end_time: str

class ProviderSnapshot(BaseModel):
    name: str
    rating: float
    review_count: int
    portfolio_samples: List[str] = []

# --- Main Models ---

class OfferCreate(BaseModel):
    request_id: UUID
    provider_id: UUID
    service_id: UUID
    service_name: str
    available_slots: List[TimeSlot]
    price: float
    currency: str = "USD"
    price_notes: Optional[str] = None
    message: Optional[str] = None
    expires_at: Optional[datetime] = None

class OfferResponse(OfferCreate):
    id: UUID
    created_at: datetime
    status: str
    provider_snapshot: Optional[ProviderSnapshot] = None
    
    model_config = ConfigDict(from_attributes=True)

class OfferUpdate(BaseModel):
    status: Optional[str] = None
