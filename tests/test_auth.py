"""
Tests for authentication requirements on protected endpoints.
"""

import pytest
from uuid import uuid4
from fastapi import status
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "sub": "user_123",
        "email": "test@example.com",
        "public_metadata": {"role": "consumer"}
    }


@pytest.fixture
def mock_provider_user():
    """Mock authenticated provider user."""
    return {
        "sub": "provider_123",
        "email": "provider@example.com",
        "public_metadata": {"role": "provider"}
    }


@pytest.fixture
def auth_headers(mock_user):
    """Authorization headers for authenticated requests."""
    return {"Authorization": "Bearer mock_token"}


@pytest.fixture
def provider_auth_headers(mock_provider_user):
    """Authorization headers for provider requests."""
    return {"Authorization": "Bearer mock_provider_token"}


class TestProviderEndpointsAuth:
    """Test authentication requirements for provider endpoints."""
    
    def test_create_provider_requires_auth(self, client):
        """POST /providers/ should require authentication."""
        response = client.post(
            "/providers/",
            json={
                "name": "Test Provider",
                "email": "test@example.com"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_service_requires_auth(self, client):
        """POST /providers/{id}/services should require authentication."""
        provider_id = uuid4()
        response = client.post(
            f"/providers/{provider_id}/services",
            json={
                "service_name": "Haircut",
                "price": 50
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_template_requires_auth(self, client):
        """POST /providers/{id}/templates should require authentication."""
        provider_id = uuid4()
        response = client.post(
            f"/providers/{provider_id}/templates",
            json={"template": "test"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_portfolio_photo_requires_auth(self, client):
        """POST /providers/{id}/portfolio should require authentication."""
        provider_id = uuid4()
        response = client.post(
            f"/providers/{provider_id}/portfolio",
            json={
                "photo_url": "https://example.com/photo.jpg",
                "caption": "Test photo"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_portfolio_photo_requires_auth(self, client):
        """PATCH /providers/{id}/portfolio/{photo_id} should require authentication."""
        provider_id = uuid4()
        photo_id = uuid4()
        response = client.patch(
            f"/providers/{provider_id}/portfolio/{photo_id}",
            json={"caption": "Updated caption"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_portfolio_photo_requires_auth(self, client):
        """DELETE /providers/{id}/portfolio/{photo_id} should require authentication."""
        provider_id = uuid4()
        photo_id = uuid4()
        response = client.delete(
            f"/providers/{provider_id}/portfolio/{photo_id}"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_service_requires_auth(self, client):
        """PATCH /providers/{id}/services/{service_id} should require authentication."""
        provider_id = uuid4()
        service_id = uuid4()
        response = client.patch(
            f"/providers/{provider_id}/services/{service_id}",
            json={"price": 60}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_service_requires_auth(self, client):
        """DELETE /providers/{id}/services/{service_id} should require authentication."""
        provider_id = uuid4()
        service_id = uuid4()
        response = client.delete(
            f"/providers/{provider_id}/services/{service_id}"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_providers_is_public(self, client):
        """GET /providers/ should be public (no auth required)."""
        response = client.get("/providers/")
        # Should not return 401, might return 200 or empty list
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
    
    def test_get_provider_profile_is_public(self, client):
        """GET /providers/{id}/profile should be public."""
        provider_id = uuid4()
        response = client.get(f"/providers/{provider_id}/profile")
        # Should not return 401, might return 404 if provider doesn't exist
        assert response.status_code != status.HTTP_401_UNAUTHORIZED


class TestOfferEndpointsAuth:
    """Test authentication requirements for offer endpoints."""
    
    def test_list_offers_requires_auth(self, client):
        """GET /offers/ should require authentication."""
        response = client.get("/offers/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_offer_requires_auth(self, client):
        """POST /offers/ should require authentication."""
        response = client.post(
            "/offers/",
            json={
                "request_id": str(uuid4()),
                "provider_id": str(uuid4()),
                "service_id": str(uuid4()),
                "service_name": "Haircut",
                "price": 50,
                "currency": "USD",
                "available_slots": []
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_accept_offer_requires_auth(self, client):
        """PUT /offers/{id}/accept should require authentication."""
        offer_id = uuid4()
        response = client.put(f"/offers/{offer_id}/accept")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_offer_requires_auth(self, client):
        """GET /offers/{id} should require authentication."""
        offer_id = uuid4()
        response = client.get(f"/offers/{offer_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestBookingEndpointsAuth:
    """Test authentication requirements for booking endpoints."""
    
    def test_get_booking_requires_auth(self, client):
        """GET /bookings/{id} should require authentication."""
        booking_id = uuid4()
        response = client.get(f"/bookings/{booking_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_complete_booking_requires_auth(self, client):
        """PUT /bookings/{id}/complete should require authentication."""
        booking_id = uuid4()
        response = client.put(f"/bookings/{booking_id}/complete")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_cancel_booking_requires_auth(self, client):
        """PUT /bookings/{id}/cancel should require authentication."""
        booking_id = uuid4()
        response = client.put(f"/bookings/{booking_id}/cancel")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestReviewEndpointsAuth:
    """Test authentication requirements for review endpoints."""
    
    def test_create_review_requires_auth(self, client):
        """POST /reviews/ should require authentication."""
        response = client.post(
            "/reviews/",
            json={
                "booking_id": str(uuid4()),
                "provider_id": str(uuid4()),
                "consumer_id": str(uuid4()),
                "rating": 5,
                "comment": "Great service!"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_provider_reviews_is_public(self, client):
        """GET /reviews/provider/{provider_id} should be public."""
        provider_id = uuid4()
        response = client.get(f"/reviews/provider/{provider_id}")
        # Should not return 401, might return empty list
        assert response.status_code != status.HTTP_401_UNAUTHORIZED


class TestEnrollmentEndpointsAuth:
    """Test authentication requirements for enrollment endpoints."""
    
    def test_start_enrollment_is_optional_auth(self, client):
        """POST /enrollment/start should support optional auth."""
        response = client.post("/enrollment/start")
        # Should not return 401 (supports guest enrollment)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
    
    def test_get_enrollment_supports_optional_auth(self, client):
        """GET /enrollment/{id} should support optional auth."""
        enrollment_id = uuid4()
        response = client.get(f"/enrollment/{enrollment_id}")
        # Should not return 401 (might return 404 if not found)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
