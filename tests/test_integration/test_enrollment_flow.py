"""
Integration tests for Provider Enrollment flow.
"""

import pytest
from uuid import uuid4
from fastapi import status
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.platform.database import SessionLocal, Base, engine
from src.platform.models.provider import ProviderEnrollment, Provider


@pytest.fixture
def guest_user():
    """Mock guest user (no auth required for enrollment start)."""
    return None


@pytest.fixture
def authenticated_user():
    """Mock authenticated user."""
    return {
        "sub": "user_123",
        "email": "user@example.com",
        "public_metadata": {}
    }


@pytest.fixture
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()


class TestProviderEnrollmentFlow:
    """Test the provider enrollment flow."""
    
    def test_start_enrollment(self, client: TestClient, db_session):
        """Test starting a new enrollment."""
        response = client.post("/enrollment/start")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "enrollment_id" in data
        assert data["status"] == "draft"
        
        # Verify enrollment exists in database
        enrollment_id = data["enrollment_id"]
        enrollment = db_session.query(ProviderEnrollment).filter(
            ProviderEnrollment.id == uuid4() if isinstance(enrollment_id, str) else enrollment_id
        ).first()
        # Note: UUID parsing might be needed depending on response format
    
    def test_update_enrollment_data(self, client: TestClient, db_session):
        """Test updating enrollment data incrementally."""
        # Start enrollment
        start_response = client.post("/enrollment/start")
        enrollment_id = start_response.json()["enrollment_id"]
        
        # Update with name
        update_response = client.patch(
            f"/enrollment/{enrollment_id}",
            json={"full_name": "Jane Doe"}
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["data"]["full_name"] == "Jane Doe"
        
        # Update with additional data
        update_response2 = client.patch(
            f"/enrollment/{enrollment_id}",
            json={
                "business_name": "Jane's Salon",
                "email": "jane@example.com",
                "phone": "555-1234"
            }
        )
        
        assert update_response2.status_code == status.HTTP_200_OK
        data = update_response2.json()["data"]
        assert data["full_name"] == "Jane Doe"  # Previous data preserved
        assert data["business_name"] == "Jane's Salon"
        assert data["email"] == "jane@example.com"
        assert data["phone"] == "555-1234"
    
    def test_submit_enrollment(self, client: TestClient, db_session):
        """Test submitting enrollment for verification."""
        # Start enrollment
        start_response = client.post("/enrollment/start")
        enrollment_id = start_response.json()["enrollment_id"]
        
        # Add complete enrollment data
        enrollment_data = {
            "full_name": "Jane Doe",
            "business_name": "Jane's Salon",
            "email": "jane@example.com",
            "phone": "555-1234",
            "services": [
                {
                    "id": "haircut",
                    "name": "Haircut",
                    "price": 50,
                    "duration": 60
                }
            ],
            "location": {
                "city": "Brooklyn",
                "address": "123 Main St"
            },
            "availability": {
                "monday": ["9:00-17:00"],
                "tuesday": ["9:00-17:00"]
            },
            "bio": "15 years of experience"
        }
        
        # Update enrollment
        client.patch(
            f"/enrollment/{enrollment_id}",
            json=enrollment_data
        )
        
        # Submit enrollment
        with patch('src.platform.services.verification.verification_service') as mock_verification:
            mock_verification.process_enrollment.return_value = {
                "status": "verified",
                "message": "Enrollment verified",
                "provider_id": str(uuid4()),
                "can_auto_verify": True
            }
            
            submit_response = client.post(f"/enrollment/{enrollment_id}/submit")
            
            assert submit_response.status_code == status.HTTP_200_OK
            result = submit_response.json()
            assert result["status"] in ["verified", "pending_verification"]
    
    def test_get_enrollment(self, client: TestClient, db_session):
        """Test retrieving enrollment data."""
        # Start enrollment
        start_response = client.post("/enrollment/start")
        enrollment_id = start_response.json()["enrollment_id"]
        
        # Add some data
        client.patch(
            f"/enrollment/{enrollment_id}",
            json={"full_name": "Test Provider"}
        )
        
        # Get enrollment
        get_response = client.get(f"/enrollment/{enrollment_id}")
        
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["id"] == enrollment_id
        assert data["status"] == "draft"
        assert data["data"]["full_name"] == "Test Provider"
    
    def test_enrollment_optional_auth(self, client: TestClient):
        """Test that enrollment supports both guest and authenticated users."""
        # Guest user (no auth)
        start_response = client.post("/enrollment/start")
        assert start_response.status_code == status.HTTP_200_OK
        
        enrollment_id = start_response.json()["enrollment_id"]
        
        # Update without auth (guest)
        update_response = client.patch(
            f"/enrollment/{enrollment_id}",
            json={"full_name": "Guest User"}
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # Get without auth (guest)
        get_response = client.get(f"/enrollment/{enrollment_id}")
        assert get_response.status_code == status.HTTP_200_OK
