from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

class RequestSummary(BaseModel):
    id: UUID
    service_type: str
    title: Optional[str] = None
    location: Dict[str, Any]
    budget: Dict[str, Any]
    status: str
    offer_count: int
    created_at: datetime

class PendingOfferPreview(BaseModel):
    price: float
    provider_name: str
    provider_rating: float

class PendingRequestSummary(RequestSummary):
    best_offer: Optional[PendingOfferPreview] = None

class ProviderSummary(BaseModel):
    id: UUID
    name: str
    rating: float

class UpcomingBookingSummary(BaseModel):
    booking_id: UUID
    request_id: UUID
    service_type: str
    provider: ProviderSummary
    scheduled_date: date
    scheduled_time: str
    location: Dict[str, Any]
    status: str

class CompletedBookingSummary(BaseModel):
    booking_id: UUID
    request_id: UUID
    service_type: str
    provider: Dict[str, Any]
    completed_at: datetime
    has_review: bool
    review_rating: Optional[float] = None

class ConsumerRequestsResponse(BaseModel):
    consumer_id: UUID
    requests: Dict[str, List[Any]]
    counts: Dict[str, int]
