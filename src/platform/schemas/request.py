from datetime import date, datetime, time
from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, condecimal, ConfigDict
from src.platform.schemas.media import StoredMedia

# --- Location ---
class RequestLocation(BaseModel):
    city: str = Field(..., examples=["New York"])
    neighborhood: Optional[str] = Field(None, examples=["Brooklyn"])
    lat: Optional[float] = Field(None, examples=[40.7128])
    lng: Optional[float] = Field(None, examples=[-74.0060])
    max_distance_km: Optional[float] = Field(None, examples=[10.0])

# --- Requirements ---
class RequestRequirements(BaseModel):
    specializations: List[str] = Field([], examples=[["haircut", "styling"]])
    description: Optional[str] = Field(None, examples=["Need a professional fade and beard trim."])

# --- Timing ---
class RequestTiming(BaseModel):
    urgency: Literal["asap", "flexible", "specific_date"] = "flexible"
    preferred_dates: Optional[List[date]] = None
    preferred_times: Optional[List[str]] = Field(None, examples=[["Morning", "Afternoon"]])
    flexibility: Optional[str] = Field(None, examples=["Can do weekends too"])

# --- Budget ---
class RequestBudget(BaseModel):
    min_price: Optional[float] = Field(None, alias="min", examples=[50.0])
    max_price: Optional[float] = Field(None, alias="max", examples=[150.0])
    currency: str = "USD"
    flexibility: Literal["strict", "somewhat_flexible", "flexible"] = "somewhat_flexible"

# --- Main Models ---

class ServiceRequestCreate(BaseModel):
    consumer_id: UUID = Field(..., examples=["550e8400-e29b-41d4-a716-446655440000"])
    raw_input: Optional[str] = Field(None, examples=["Looking for a haircut today"])
    service_category: str = Field(..., examples=["Hair & Beauty"])
    service_type: str = Field(..., examples=["Men's Haircut"])
    requirements: RequestRequirements
    location: RequestLocation
    timing: RequestTiming
    budget: RequestBudget
    media: List[StoredMedia] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "consumer_id": "550e8400-e29b-41d4-a716-446655440000",
                "raw_input": "I need a professional haircut and beard trim in Brooklyn.",
                "service_category": "Hair & Beauty",
                "service_type": "Men's Haircut",
                "requirements": {
                    "specializations": ["Beard Trim", "Fade"],
                    "description": "Mid-fade with a square back."
                },
                "location": {
                    "city": "New York",
                    "neighborhood": "Brooklyn",
                    "lat": 40.7128,
                    "lng": -74.0060
                },
                "timing": {
                    "urgency": "specific_date",
                    "preferred_dates": ["2026-02-01"],
                    "preferred_times": ["Afternoon"]
                },
                "budget": {
                    "min": 40,
                    "max": 100,
                    "currency": "USD"
                }
            }
        }
    )

class ServiceRequestResponse(ServiceRequestCreate):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    status_history: List[dict] = []  # Sprint 10: Timeline tracking
    matched_providers: List[UUID] = []
    viewed_by_current_provider: Optional[bool] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
