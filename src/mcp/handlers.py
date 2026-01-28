from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, time, date

from src.platform.database import SessionLocal
from src.platform.models.booking import Booking
from src.platform.models.offer import Offer
from src.platform.models.provider import Provider
from src.platform.models.request import ServiceRequest
from src.platform.models.review import Review
from src.platform.models.service import Service
from src.platform.services.matching import MatchingService
from src.platform.metrics import track_request_created, track_offer_submitted, track_booking_confirmed

# --- Consumer Handlers ---

def create_service_request(
    consumer_id: UUID,
    service_category: str,
    service_type: str,
    raw_input: str,
    requirements: Dict[str, Any],
    location: Dict[str, Any],
    timing: Dict[str, Any],
    budget: Dict[str, Any],
    media: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    with SessionLocal() as db:
        # Create Request
        req = ServiceRequest(
            id=uuid4(),
            consumer_id=consumer_id,
            raw_input=raw_input,
            service_category=service_category,
            service_type=service_type,
            requirements=requirements,
            location=location,
            timing=timing,
            budget=budget,
            media=media,
            status="matching"
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        
        # Trigger Matching
        matcher = MatchingService(db)
        # Note: Matcher expects Pydantic object usually, but let's check implementation. 
        # In matching.py, it accessed attributes like .service_type. 
        # The DB model also has these attributes. It might just work if duck-typed.
        # But wait, matching.py accessed request_data.location.city (pydantic style)
        # DB model location is a dict. So Providers.location['city'] vs dict access.
        # The current matching.py does `request_data.location.city`.
        # If I pass the DB model, `req.location` is a dict. `req.location.city` will fail.
        # I should construct a schema object or update matching.py to handle both.
        # For safety/speed, let's just make a simple object wrapper or modify matching logic slightly?
        # Re-reading matching.py: it uses `request_data.location.city`.
        
        # Let's create a temporary object that mimics the structure needed
        class SimpleObj:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
        
        # Or better, just import the schema
        from src.platform.schemas.request import ServiceRequestCreate, RequestLocation, RequestRequirements, RequestTiming, RequestBudget
        
        schema = ServiceRequestCreate(
            consumer_id=consumer_id,
            raw_input=raw_input,
            service_category=service_category,
            service_type=service_type,
            requirements=RequestRequirements(**requirements),
            location=RequestLocation(**location),
            timing=RequestTiming(**timing),
            budget=RequestBudget(**budget),
            media=media
        )
        
        matched_ids = matcher.find_providers(schema)
        req.matched_providers = [str(uid) for uid in matched_ids]
        
        db.commit()
        
        # Track metric
        track_request_created(service_category)
        
        return {
            "request_id": str(req.id),
            "status": req.status,
            "message": f"Request created. Found {len(matched_ids)} matching providers."
        }

def get_offers(request_id: UUID) -> Dict[str, Any]:
    with SessionLocal() as db:
        offers = db.query(Offer).filter(Offer.request_id == request_id).all()
        
        result_offers = []
        for o in offers:
            result_offers.append({
                "offer_id": str(o.id),
                "service_name": o.service_name,
                "price": o.price,
                "available_slots": o.available_slots,
                "provider_snapshot": o.provider_snapshot,
                "message": o.message
            })
            
        return {"offers": result_offers}

def accept_offer(offer_id: UUID, selected_slot: Dict[str, Any]) -> Dict[str, Any]:
    with SessionLocal() as db:
        offer = db.query(Offer).filter(Offer.id == offer_id).first()
        if not offer:
            return {"error": "Offer not found"}
            
        if offer.status != "pending":
            return {"error": f"Offer is {offer.status}"}
            
        req = db.query(ServiceRequest).filter(ServiceRequest.id == offer.request_id).first()
        
        # Update statuses
        offer.status = "accepted"
        req.status = "booked"
        req.selected_offer_id = offer.id
        
        # Create Booking
        booking_id = uuid4()
        
        # Parse slot
        s_date = datetime.strptime(selected_slot['date'], "%Y-%m-%d").date()
        s_start = datetime.strptime(selected_slot['start_time'], "%H:%M").time()
        # Assume 1 hour if end not provided, or fetch from offer slots logic
        # For MVP, assume end time is passed or calculated. 
        # The Spec only sends date/start_time.
        # Let's verify against the slot list in the offer to find end time.
        s_end = None
        for slot in offer.available_slots:
            if slot['date'] == selected_slot['date'] and slot['start_time'] == selected_slot['start_time']:
                s_end = datetime.strptime(slot['end_time'], "%H:%M").time()
                break
        
        if not s_end:
             # Fallback 1 hour
             s_end = (datetime.combine(date.today(), s_start) + __import__('timedelta').timedelta(hours=1)).time()

        booking = Booking(
            id=booking_id,
            request_id=req.id,
            offer_id=offer.id,
            provider_id=offer.provider_id,
            consumer_id=req.consumer_id,
            service_id=offer.service_id,
            service_name=offer.service_name,
            scheduled_date=s_date,
            scheduled_start=s_start,
            scheduled_end=s_end,
            timezone="UTC",
            location={"type": "provider_location"}, # Simplified
            price=offer.price,
            currency=offer.currency,
            status="confirmed"
        )
        
        db.add(booking)
        db.commit()
        
        # Track metric
        track_booking_confirmed(req.service_category)
        
        return {
            "booking_id": str(booking.id),
            "status": "confirmed"
        }

def submit_review(booking_id: UUID, rating: int, comment: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return {"error": "Booking not found"}
            
        review = Review(
            id=uuid4(),
            booking_id=booking.id,
            provider_id=booking.provider_id,
            consumer_id=booking.consumer_id,
            rating=rating,
            comment=comment,
            visible=True
        )
        db.add(review)
        db.commit()
        return {"review_id": str(review.id), "status": "submitted"}

# --- Provider Handlers ---

def get_matching_requests(provider_id: UUID) -> List[Dict[str, Any]]:
    with SessionLocal() as db:
        # Find requests where matched_providers contains this provider_id
        # matched_providers is a JSONB list of strings
        # Query:
        requests = db.query(ServiceRequest).filter(
            ServiceRequest.status == "matching"
            # In python check for simplicity unless using pg operators
        ).all()
        
        matches = []
        pid_str = str(provider_id)
        for r in requests:
            if r.matched_providers and pid_str in r.matched_providers:
                matches.append({
                    "request_id": str(r.id),
                    "service_type": r.service_type,
                    "location": r.location,
                    "timing": r.timing,
                    "budget": r.budget
                })
        return matches

def submit_offer(
    request_id: UUID,
    provider_id: UUID,
    price: float,
    available_slots: List[Dict[str, str]],
    message: str
) -> Dict[str, Any]:
    with SessionLocal() as db:
        req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not req:
            return {"error": "Request not found"}
            
        offer = Offer(
            id=uuid4(),
            request_id=request_id,
            provider_id=provider_id,
            service_name=req.service_type, # Simplified
            price=price,
            message=message,
            available_slots=available_slots,
            status="pending"
        )
        db.add(offer)
        
        if req.status == "matching":
            req.status = "offers_received"
            
        db.commit()
        
        # Track metric
        track_offer_submitted(req.service_category)
        
        return {"offer_id": str(offer.id), "status": "submitted"}

def get_provider(provider_id: UUID) -> Dict[str, Any]:
    with SessionLocal() as db:
        p = db.query(Provider).filter(Provider.id == provider_id).first()
        if not p:
            return {"error": "Provider not found"}
        return {
            "id": str(p.id),
            "name": p.name,
            "specializations": p.specializations,
            "availability": p.availability,
            "offer_templates": p.offer_templates,
            "rating": p.rating,
            "status": p.status
        }

def mark_lead_viewed(provider_id: UUID, request_id: UUID) -> Dict[str, Any]:
    from src.platform.models.provider import ProviderLeadView
    with SessionLocal() as db:
        existing = db.query(ProviderLeadView).filter(
            ProviderLeadView.provider_id == provider_id,
            ProviderLeadView.request_id == request_id
        ).first()
        
        if not existing:
            view = ProviderLeadView(
                id=uuid4(),
                provider_id=provider_id,
                request_id=request_id
            )
            db.add(view)
            db.commit()
            return {"status": "marked_viewed"}
        return {"status": "already_viewed"}
