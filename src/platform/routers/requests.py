from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

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
    from datetime import datetime
    db_request = ServiceRequest(
        consumer_id=request.consumer_id,
        raw_input=request.raw_input,
        service_category=request.service_category,
        service_type=request.service_type,
        requirements=request.requirements.model_dump(),
        location=request.location.model_dump(),
        timing=request.timing.model_dump(),
        budget=request.budget.model_dump(),
        status="matching",
        status_history=[{
            "status": "matching",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Request created"
        }]
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
    matching_provider_id: UUID = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List service requests, optionally filtered by status or matched provider.
    """
    query = db.query(ServiceRequest)
    if status:
        query = query.filter(ServiceRequest.status == status)
    
    if matching_provider_id:
        # PostgreSQL specific JSONB contains @> ['uuid-string']
        # For SQLite/Mocks, we'll do literal check
        pid_str = str(matching_provider_id)
        # SQLAlchemy simplified check for JSON column
        query = query.filter(cast(ServiceRequest.matched_providers, String).contains(pid_str))

    requests = query.offset(skip).limit(limit).all()
    
    if matching_provider_id:
        from src.platform.models.provider import ProviderLeadView
        # Fetch viewed IDs for this provider
        viewed_ids = {
            v.request_id for v in db.query(ProviderLeadView).filter(
                ProviderLeadView.provider_id == matching_provider_id
            ).all()
        }
        
        # We need to add viewed field to response. 
        # Since response_model is ServiceRequestResponse, we might need a wrapper or dynamic field.
        # For now, let's just return them and hope the schema allows extra fields or we update schema.
        for r in requests:
            r.viewed_by_current_provider = r.id in viewed_ids
            
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

@router.put("/{request_id}/view")
def mark_request_viewed(request_id: UUID, provider_id: UUID, db: Session = Depends(get_db)):
    """
    Mark a request as viewed by a specific provider.
    """
    from src.mcp.handlers import mark_lead_viewed
    # Using handler since we already defined logic there
    return mark_lead_viewed(provider_id, request_id)

# Sprint 10: Request Details & Management

@router.patch("/{request_id}", response_model=ServiceRequestResponse)
def update_request(request_id: UUID, updates: dict, db: Session = Depends(get_db)):
    """
    Update a service request. Only allowed for requests in 'matching' status with no offers.
    """
    from datetime import datetime
    from sqlalchemy.orm.attributes import flag_modified
    
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check if editing is allowed
    offer_count = db.query(Offer).filter(Offer.request_id == request_id).count()
    if req.status != "matching" or offer_count > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot edit request. Request must be in 'matching' status with no offers."
        )
    
    # Update allowed fields
    allowed_fields = ["requirements", "location", "timing", "budget", "service_category", "service_type"]
    for field, value in updates.items():
        if field in allowed_fields and hasattr(req, field):
            setattr(req, field, value)
    
    # Add to status history
    if not req.status_history:
        req.status_history = []
    req.status_history.append({
        "status": req.status,
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Request updated"
    })
    flag_modified(req, "status_history")
    
    db.commit()
    db.refresh(req)
    return req

@router.post("/{request_id}/cancel", response_model=ServiceRequestResponse)
def cancel_request(request_id: UUID, db: Session = Depends(get_db)):
    """
    Cancel a service request. Only allowed for requests in 'matching' or 'pending' status.
    """
    from datetime import datetime
    from sqlalchemy.orm.attributes import flag_modified
    
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check if cancellation is allowed
    if req.status not in ["matching", "pending"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel request in '{req.status}' status. Only 'matching' or 'pending' requests can be canceled."
        )
    
    # Update status
    old_status = req.status
    req.status = "cancelled"
    
    # Add to status history
    if not req.status_history:
        req.status_history = []
    req.status_history.append({
        "status": "cancelled",
        "timestamp": datetime.utcnow().isoformat(),
        "note": f"Request cancelled (was {old_status})"
    })
    flag_modified(req, "status_history")
    
    db.commit()
    db.refresh(req)
    return req
