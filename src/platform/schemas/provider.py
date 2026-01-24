from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from uuid import UUID

# --- Location Models ---

class Coordinates(BaseModel):
    lat: float
    lng: float

class Location(BaseModel):
    address: Optional[str] = None
    city: str
    neighborhood: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    service_radius_km: Optional[float] = None

# --- Availability Models ---

class TimeRange(BaseModel):
    start: str  # Format "HH:MM"
    end: str    # Format "HH:MM"

class Schedule(BaseModel):
    monday: List[TimeRange] = []
    tuesday: List[TimeRange] = []
    wednesday: List[TimeRange] = []
    thursday: List[TimeRange] = []
    friday: List[TimeRange] = []
    saturday: List[TimeRange] = []
    sunday: List[TimeRange] = []

class Availability(BaseModel):
    timezone: str = "UTC"
    schedule: Schedule = Field(default_factory=Schedule)
    exceptions: List[Any] = []

# --- Settings ---

class ProviderSettings(BaseModel):
    auto_accept: bool = False
    min_notice_hours: int = 24
    max_bookings_per_day: Optional[int] = None
    instant_booking: bool = False

# --- Core Provider Models ---

class ProviderBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    location: Optional[Location] = None
    specializations: List[str] = []
    availability: Optional[Availability] = None
    settings: ProviderSettings = Field(default_factory=ProviderSettings)
    status: str = "active"

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    location: Optional[Location] = None
    specializations: Optional[List[str]] = None
    availability: Optional[Availability] = None
    settings: Optional[ProviderSettings] = None
    status: Optional[str] = None

class ProviderResponse(ProviderBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    verified: bool
    rating: float
    review_count: int
    completed_bookings: int

    class Config:
        from_attributes = True
