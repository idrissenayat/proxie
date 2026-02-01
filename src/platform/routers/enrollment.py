from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.platform.database import get_db
from src.platform.models.provider import ProviderEnrollment
from src.platform.auth import get_optional_user
from typing import Dict, Any, Optional

router = APIRouter(
    prefix="/enrollment",
    tags=["enrollment"],
)

@router.post("/start")
def start_enrollment(db: Session = Depends(get_db)):
    """Initialize a new provider enrollment."""
    enrollment = ProviderEnrollment(
        id=uuid4(),
        status="draft",
        data={}
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return {"enrollment_id": enrollment.id, "status": enrollment.status}

@router.get("/{id}")
def get_enrollment(
    id: UUID,
    db: Session = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get current enrollment data."""
    enrollment = db.query(ProviderEnrollment).filter(ProviderEnrollment.id == id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment

@router.patch("/{id}")
def update_enrollment(
    id: UUID,
    data_update: Dict[str, Any],
    db: Session = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Update enrollment data."""
    from sqlalchemy.orm.attributes import flag_modified
    
    enrollment = db.query(ProviderEnrollment).filter(ProviderEnrollment.id == id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Merge data - need to copy to trigger change detection
    current_data = dict(enrollment.data or {})
    current_data.update(data_update)
    enrollment.data = current_data
    flag_modified(enrollment, "data")
    
    db.commit()
    db.refresh(enrollment)
    return enrollment

@router.post("/{id}/submit")
def submit_enrollment(
    id: UUID,
    db: Session = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Submit enrollment for verification."""
    enrollment = db.query(ProviderEnrollment).filter(ProviderEnrollment.id == id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    enrollment.status = "pending"
    db.commit()
    
    # In a real app, this would trigger background verification
    # For MVP, we'll implement a service to handle this.
    from src.platform.services.verification import verification_service
    return verification_service.process_enrollment(enrollment, db)
