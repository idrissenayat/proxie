from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = "USD"

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: UUID
    provider_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
