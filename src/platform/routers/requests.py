from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.platform.database import get_db
from src.platform.models.request import ServiceRequest
from src.platform.schemas.request import ServiceRequestCreate, ServiceRequestResponse
from src.platform.services.matching import MatchingService
from src.platform.models.offer import Offer
from src.platform.schemas.offer import OfferResponse

router = APIRouter(
    prefix="/requests",
    tags=["requests"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request: ServiceRequestCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new service request and trigger matching.
    """
    # 1. Create Request Record
    request_data = request.model_dump()
    # Convert Pydantic models to dicts for JSON fields
    db_request = ServiceRequest(
        consumer_id=request.consumer_id,
        raw_input=request.raw_input,
        service_category=request.service_category,
        service_type=request.service_type,
        requirements=request.requirements.model_dump(),
        location=request.location.model_dump(),
        timing=request.timing.model_dump(),
        budget=request.budget.model_dump(),
        status="matching"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # 2. Trigger Matching
    matcher = MatchingService(db)
    matched_ids = matcher.find_providers(request)
    
    # 3. Update Request with Matches
    # specific UUID serialization handling might be needed depending on DB driver, 
    # but usually list of UUIDs is fine if JSON serializer handles it. 
    # Safest is to convert to strings.
    matched_ids_str = [str(uid) for uid in matched_ids]
    
    db_request.matched_providers = matched_ids_str
    if matched_ids:
        # In a real system, we would notify providers here
        pass
        
    db.commit()
    db.refresh(db_request)
    
    return db_request

@router.get("/", response_model=List[ServiceRequestResponse])
def list_requests(
    status: str = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List service requests, optionally filtered by status.
    """
    query = db.query(ServiceRequest)
    if status:
        query = query.filter(ServiceRequest.status == status)
    
    requests = query.offset(skip).limit(limit).all()
    return requests

@router.get("/{request_id}", response_model=ServiceRequestResponse)
def get_request(request_id: UUID, db: Session = Depends(get_db)):
    """
    Get request details.
    """
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req

@router.post("/{request_id}/match", response_model=ServiceRequestResponse)
def trigger_matching(request_id: UUID, db: Session = Depends(get_db)):
    """
    Manually re-trigger matching for a request.
    """
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    # Reconstruct the schema object for the matcher (partial reconstruction)
    # This is a bit hacky, ideally matcher takes model or we have a shared DTO
    # For now, we fetch details from the model.
    # Note: MatchingService expects ServiceRequestCreate schema currently.
    # We'll instantiate it from the DB model.
    
    from src.platform.schemas.request import RequestRequirements, RequestLocation, RequestTiming, RequestBudget
    
    schema = ServiceRequestCreate(
        consumer_id=req.consumer_id,
        raw_input=req.raw_input,
        service_category=req.service_category,
        service_type=req.service_type,
        requirements=RequestRequirements(**req.requirements),
        location=RequestLocation(**req.location),
        timing=RequestTiming(**req.timing),
        budget=RequestBudget(**req.budget)
    )
    
    matcher = MatchingService(db)
    matched_ids = matcher.find_providers(schema)
    matched_ids_str = [str(uid) for uid in matched_ids]
    
    req.matched_providers = matched_ids_str
    db.commit()
    db.refresh(req)
    
    return req

@router.get("/{request_id}/offers", response_model=List[OfferResponse])
def get_request_offers(request_id: UUID, db: Session = Depends(get_db)):
    """
    Get all offers for a specific request.
    """
    offers = db.query(Offer).filter(Offer.request_id == request_id).all()
    return offers
