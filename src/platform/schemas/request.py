from datetime import date, datetime, time
from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, condecimal

# --- Location ---
class RequestLocation(BaseModel):
    city: str
    neighborhood: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    max_distance_km: Optional[float] = None

# --- Requirements ---
class RequestRequirements(BaseModel):
    specializations: List[str] = []
    description: Optional[str] = None

# --- Timing ---
class RequestTiming(BaseModel):
    urgency: Literal["asap", "flexible", "specific_date"] = "flexible"
    preferred_dates: Optional[List[date]] = None
    preferred_times: Optional[List[str]] = None
    flexibility: Optional[str] = None

# --- Budget ---
class RequestBudget(BaseModel):
    min_price: Optional[float] = Field(None, alias="min")
    max_price: Optional[float] = Field(None, alias="max")
    currency: str = "USD"
    flexibility: Literal["strict", "somewhat_flexible", "flexible"] = "somewhat_flexible"

# --- Main Models ---

class ServiceRequestCreate(BaseModel):
    consumer_id: UUID
    raw_input: Optional[str] = None
    service_category: str
    service_type: str
    requirements: RequestRequirements
    location: RequestLocation
    timing: RequestTiming
    budget: RequestBudget

class ServiceRequestResponse(ServiceRequestCreate):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    matched_providers: List[UUID] = []
    
    class Config:
        from_attributes = True
        populate_by_name = True
