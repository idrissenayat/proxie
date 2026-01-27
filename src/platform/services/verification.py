from typing import Dict, Any
from sqlalchemy.orm import Session
from src.platform.models.provider import Provider, ProviderEnrollment
from src.platform.services.catalog import catalog_service

class VerificationService:
    def process_enrollment(self, enrollment: ProviderEnrollment, db: Session):
        """Analyze enrollment and auto-verify if possible."""
        data = enrollment.data or {}
        
        # 1. Check for completeness
        required_fields = ["full_name", "services", "location", "availability"]
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            return {
                "status": "pending",
                "message": f"Enrollment incomplete. Missing: {', '.join(missing)}",
                "can_auto_verify": False
            }

        # 2. Check for licensed services
        requires_manual = False
        for svc_entry in data.get("services", []):
            svc_id = svc_entry.get("service_id")
            svc_meta = catalog_service.get_service(svc_id)
            if svc_meta and svc_meta.get("requires_license"):
                requires_manual = True
                break
        
        # 3. Check portfolio
        portfolio = data.get("portfolio", [])
        if len(portfolio) < 3:
            # We allow basic services without portfolio for some categories, 
            # but PRD says 3+ recommended.
            # For now, let's keep it as a suggestion in the message but allow activation if not licensed.
            pass

        if requires_manual:
            enrollment.status = "pending_verification"
            db.commit()
            return {
                "status": "pending_verification",
                "message": "Your selected services require manual license verification. We'll review your profile within 24 hours.",
                "can_auto_verify": False
            }

        # 4. Auto-verify and activate
        return self.activate_provider(enrollment, db)

    def activate_provider(self, enrollment: ProviderEnrollment, db: Session):
        """Create a permanent Provider record from enrollment data."""
        data = enrollment.data
        
        # Check if provider already exists by email
        existing = db.query(Provider).filter(Provider.email == data["email"]).first()
        if existing:
            provider = existing
        else:
            provider = Provider(
                name=data["full_name"],
                email=data["email"],
                phone=data.get("phone"),
                verified=True,
                status="active"
            )
            db.add(provider)
            db.flush()

        # Update provider details
        provider.bio = data.get("bio")
        provider.profile_photo_url = data.get("profile_photo_url")
        provider.location = data.get("location")
        provider.availability = data.get("availability")
        
        # Specializations from services
        specs = []
        for s in data.get("services", []):
            if "specializations" in s:
                specs.extend(s["specializations"])
        provider.specializations = list(set(specs))
        
        # Link enrollment
        enrollment.status = "verified"
        enrollment.provider_id = provider.id
        
        db.commit()
        
        return {
            "status": "verified",
            "message": "Congratulations! Your profile is verified and active. You can now start receiving leads.",
            "provider_id": str(provider.id)
        }

verification_service = VerificationService()
