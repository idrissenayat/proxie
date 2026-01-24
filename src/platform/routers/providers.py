from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.platform.database import get_db
from src.platform.models.provider import Provider
from src.platform.models.service import Service
from src.platform.schemas.provider import ProviderCreate, ProviderResponse, ProviderUpdate
from src.platform.schemas.service import ServiceCreate, ServiceResponse

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[ProviderResponse])
def list_providers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List providers with pagination."""
    providers = db.query(Provider).offset(skip).limit(limit).all()
    return providers

@router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(provider: ProviderCreate, db: Session = Depends(get_db)):
    """Create a new provider."""
    # Check if email exists
    db_provider = db.query(Provider).filter(Provider.email == provider.email).first()
    if db_provider:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Convert Pydantic model to dict
    provider_data = provider.model_dump()
    
    new_provider = Provider(**provider_data)
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return new_provider

@router.get("/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: UUID, db: Session = Depends(get_db)):
    """Get a specific provider by ID."""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.put("/{provider_id}", response_model=ProviderResponse)
def update_provider(
    provider_id: UUID, 
    provider_update: ProviderUpdate, 
    db: Session = Depends(get_db)
):
    """Update a provider's information."""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    update_data = provider_update.model_dump(exclude_unset=True)
    
    if "email" in update_data and update_data["email"] != provider.email:
        existing_email = db.query(Provider).filter(Provider.email == update_data["email"]).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already in use")
    
    for key, value in update_data.items():
        setattr(provider, key, value)
        
    db.commit()
    db.refresh(provider)
    return provider

# --- Service Endpoints ---

@router.post("/{provider_id}/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_provider_service(
    provider_id: UUID,
    service: ServiceCreate,
    db: Session = Depends(get_db)
):
    """Add a service to a provider."""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    new_service = Service(
        provider_id=provider_id,
        **service.model_dump()
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.get("/{provider_id}/services", response_model=List[ServiceResponse])
def list_provider_services(
    provider_id: UUID,
    db: Session = Depends(get_db)
):
    """List all services for a provider."""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    # Assuming relationship or query
    # We didn't define relationship in model explicitly, so direct query:
    services = db.query(Service).filter(Service.provider_id == provider_id).all()
    return services
