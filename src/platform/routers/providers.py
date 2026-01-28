from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.platform.database import get_db
from src.platform.models.provider import Provider, ProviderPortfolioPhoto
from src.platform.models.service import Service
from src.platform.schemas.provider import (
    ProviderCreate, ProviderResponse, ProviderUpdate,
    PortfolioPhotoCreate, PortfolioPhotoUpdate, PortfolioPhotoResponse,
    ProfileUpdate
)
from src.platform.schemas.service import ServiceCreate, ServiceResponse
from src.platform.auth import get_current_user

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
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a provider's information."""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    # Security: Ensure user owns this provider record (or is admin)
    if provider.clerk_id != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this profile")
        
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

@router.post("/{provider_id}/templates", response_model=ProviderResponse)
def add_offer_template(
    provider_id: UUID, 
    template: dict, # Simplified schema for MVP
    db: Session = Depends(get_db)
):
    """Add an offer template to a provider."""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    current_templates = list(provider.offer_templates) if provider.offer_templates else []
    current_templates.append(template)
    provider.offer_templates = current_templates
    
    db.commit()
    db.refresh(provider)
    return provider

# --- Sprint 10: Provider Profile Management ---

@router.get("/{provider_id}/profile", response_model=ProviderResponse)
def get_provider_profile(provider_id: UUID, db: Session = Depends(get_db)):
    """
    Get public provider profile with all details including stats.
    This is the consumer-facing view.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.patch("/{provider_id}/profile", response_model=ProviderResponse)
def update_provider_profile(
    provider_id: UUID,
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update provider's own profile. Provider can edit their profile information.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Security Check
    if provider.clerk_id != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this profile")
    
    # Update profile fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(provider, key, value)
    
    db.commit()
    db.refresh(provider)
    return provider

# --- Sprint 10: Portfolio Management ---

@router.get("/{provider_id}/portfolio", response_model=List[PortfolioPhotoResponse])
def get_provider_portfolio(provider_id: UUID, db: Session = Depends(get_db)):
    """
    Get all portfolio photos for a provider, ordered by display_order.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    photos = db.query(ProviderPortfolioPhoto).filter(
        ProviderPortfolioPhoto.provider_id == provider_id
    ).order_by(ProviderPortfolioPhoto.display_order).all()
    
    return photos

@router.post("/{provider_id}/portfolio", response_model=PortfolioPhotoResponse, status_code=status.HTTP_201_CREATED)
def add_portfolio_photo(
    provider_id: UUID,
    photo: PortfolioPhotoCreate,
    db: Session = Depends(get_db)
):
    """
    Add a new photo to provider's portfolio.
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    new_photo = ProviderPortfolioPhoto(
        provider_id=provider_id,
        **photo.model_dump()
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo

@router.patch("/{provider_id}/portfolio/{photo_id}", response_model=PortfolioPhotoResponse)
def update_portfolio_photo(
    provider_id: UUID,
    photo_id: UUID,
    photo_update: PortfolioPhotoUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a portfolio photo's caption or display order.
    """
    photo = db.query(ProviderPortfolioPhoto).filter(
        ProviderPortfolioPhoto.id == photo_id,
        ProviderPortfolioPhoto.provider_id == provider_id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Portfolio photo not found")
    
    update_data = photo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(photo, key, value)
    
    db.commit()
    db.refresh(photo)
    return photo

@router.delete("/{provider_id}/portfolio/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_photo(
    provider_id: UUID,
    photo_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a portfolio photo.
    """
    photo = db.query(ProviderPortfolioPhoto).filter(
        ProviderPortfolioPhoto.id == photo_id,
        ProviderPortfolioPhoto.provider_id == provider_id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Portfolio photo not found")
    
    db.delete(photo)
    db.commit()
    return None

# --- Sprint 10: Service Management (Extended) ---

@router.patch("/{provider_id}/services/{service_id}", response_model=ServiceResponse)
def update_provider_service(
    provider_id: UUID,
    service_id: UUID,
    service_update: dict,  # Simplified for MVP
    db: Session = Depends(get_db)
):
    """
    Update a provider's service.
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.provider_id == provider_id
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    for key, value in service_update.items():
        if hasattr(service, key):
            setattr(service, key, value)
    
    db.commit()
    db.refresh(service)
    return service

@router.delete("/{provider_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider_service(
    provider_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a provider's service.
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.provider_id == provider_id
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db.delete(service)
    db.commit()
    return None
