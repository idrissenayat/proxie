"""
Tests for resource ownership validation.
"""

import pytest
from uuid import UUID, uuid4
from datetime import date, datetime, time
from fastapi import status
from unittest.mock import patch, MagicMock
from src.platform.main import fastapi_app
from src.platform.auth import get_current_user, require_role, get_optional_user
from src.platform.database import get_db

# Real UUIDs for tests
USER_ID = str(uuid4())
OTHER_USER_ID = str(uuid4())
ADMIN_ID = str(uuid4())


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "sub": USER_ID,
        "email": "user@example.com",
        "public_metadata": {}
    }


@pytest.fixture
def mock_other_user():
    """Mock different authenticated user."""
    return {
        "sub": OTHER_USER_ID,
        "email": "other@example.com",
        "public_metadata": {}
    }


@pytest.fixture
def mock_admin_user():
    """Mock admin user."""
    return {
        "sub": ADMIN_ID,
        "email": "admin@example.com",
        "public_metadata": {"role": "admin"}
    }


def create_mock_provider(provider_id=None, clerk_id=USER_ID):
    """Create a mock provider object that satisfies Pydantic validation."""
    mock = MagicMock()
    mock.id = provider_id or uuid4()
    mock.clerk_id = clerk_id
    mock.name = "Mock Provider"
    mock.email = "mock@example.com"
    mock.phone = "555-1212"
    mock.bio = "Mock Bio"
    mock.business_name = "Mock Biz"
    mock.profile_photo_url = "http://example.com/photo.jpg"
    mock.years_experience = 5
    mock.location = {"city": "New York", "neighborhood": "SoHo", "service_radius_km": 10}
    mock.specializations = []
    mock.availability = {
        "timezone": "UTC", 
        "schedule": {
            "monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": [], "saturday": [], "sunday": []
        }
    }
    mock.settings = {"auto_accept": False, "min_notice_hours": 24}
    mock.offer_templates = []
    mock.status = "active"
    mock.verified = False
    mock.rating = 0.0
    mock.review_count = 0
    mock.completed_bookings = 0
    mock.jobs_completed = 0
    mock.response_rate = 100.0
    mock.average_response_time_hours = 1.0
    mock.created_at = datetime.now()
    mock.updated_at = datetime.now()
    return mock

def create_mock_request(request_id=None, consumer_id=USER_ID):
    """Create a mock request object that satisfies Pydantic validation."""
    mock = MagicMock()
    mock.id = request_id or uuid4()
    mock.consumer_id = UUID(consumer_id) if isinstance(consumer_id, str) else consumer_id
    mock.raw_input = "I need a haircut"
    mock.service_category = "Hair & Beauty"
    mock.service_type = "Men's Haircut"
    mock.requirements = {"specializations": [], "description": "test"}
    mock.location = {"city": "New York", "neighborhood": "SoHo"}
    mock.timing = {"urgency": "flexible"}
    mock.budget = {"min": 50, "max": 100, "currency": "USD", "flexibility": "flexible"}
    mock.status = "matching"
    mock.created_at = datetime.now()
    mock.status_history = []
    mock.matched_providers = []
    return mock

def create_mock_booking(booking_id=None, consumer_id=USER_ID, provider_id=None):
    """Create a mock booking object that satisfies Pydantic validation."""
    mock = MagicMock()
    mock.id = booking_id or uuid4()
    mock.consumer_id = UUID(consumer_id) if isinstance(consumer_id, str) else consumer_id
    mock.provider_id = provider_id or uuid4()
    mock.offer_id = uuid4()
    mock.request_id = uuid4()
    mock.service_id = uuid4()
    mock.service_name = "Mock Service"
    mock.status = "confirmed"
    mock.price = 100.0
    mock.currency = "USD"
    mock.scheduled_date = date(2025, 1, 1)
    mock.scheduled_start = time(10, 0)
    mock.scheduled_end = time(11, 0)
    mock.timezone = "UTC"
    mock.location = {"type": "consumer_location", "address": "123 Main St"}
    mock.created_at = datetime.now()
    mock.updated_at = datetime.now()
    return mock


class TestProviderOwnership:
    """Test provider resource ownership validation."""
    
    def test_user_cannot_modify_other_provider_profile(self, client, mock_user, mock_other_user):
        """User should not be able to modify another provider's profile."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=False):
                mock_db = MagicMock()
                mock_provider = create_mock_provider(provider_id, OTHER_USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_provider
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db
                
                response = client.patch(
                    f"/providers/{provider_id}/profile",
                    json={"bio": "Updated bio"},
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_user_can_modify_own_provider_profile(self, client, mock_user):
        """User should be able to modify their own provider profile."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=True):
                mock_db = MagicMock()
                mock_provider = create_mock_provider(provider_id, USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_provider
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db
                
                response = client.patch(
                    f"/providers/{provider_id}/profile",
                    json={"bio": "Updated bio"},
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_200_OK
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_admin_can_modify_any_provider_profile(self, client, mock_admin_user):
        """Admin should be able to modify any provider profile."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_admin_user
        try:
            mock_db = MagicMock()
            mock_provider = create_mock_provider(provider_id, OTHER_USER_ID)
            mock_db.query.return_value.filter.return_value.first.return_value = mock_provider
            fastapi_app.dependency_overrides[get_db] = lambda: mock_db

            response = client.patch(
                f"/providers/{provider_id}/profile",
                json={"bio": "Updated bio"},
                headers={"Authorization": "Bearer mock_token"}
            )
            assert response.status_code == status.HTTP_200_OK
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_user_cannot_add_service_to_other_provider(self, client, mock_user):
        """User should not be able to add services to another provider."""
        provider_id = uuid4()
        
        # We need mock_user to have provider role to pass require_role("provider")
        mock_user["public_metadata"]["role"] = "provider"
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=False):
                mock_db = MagicMock()
                mock_provider = create_mock_provider(provider_id, OTHER_USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_provider
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                # Endpoint: POST /providers/{provider_id}/services
                response = client.post(
                    f"/providers/{provider_id}/services",
                    json={
                        "name": "Haircut", 
                        "description": "Test",
                        "price_min": 50,
                        "price_max": 100,
                        "duration_minutes": 30
                    },
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}


class TestRequestOwnership:
    """Test service request ownership validation."""
    
    def test_user_cannot_modify_other_user_request(self, client, mock_user, mock_other_user):
        """User should not be able to modify another user's request."""
        request_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=False):
                mock_db = MagicMock()
                mock_request = create_mock_request(request_id, OTHER_USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_request
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                response = client.patch(
                    f"/requests/{request_id}",
                    json={"requirements": {"description": "updated"}},
                    headers={"Authorization": "Bearer mock_token"}
                )
                # It fails at require_ownership
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_user_can_modify_own_request(self, client, mock_user):
        """User should be able to modify their own request."""
        request_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=True):
                mock_db = MagicMock()
                mock_request = create_mock_request(request_id, USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_request
                mock_db.query.return_value.filter.return_value.count.return_value = 0
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                response = client.patch(
                    f"/requests/{request_id}",
                    json={"requirements": {"description": "updated"}},
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_200_OK
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_user_cannot_cancel_other_user_request(self, client, mock_user):
        """User should not be able to cancel another user's request."""
        request_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=False):
                mock_db = MagicMock()
                mock_request = create_mock_request(request_id, OTHER_USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_request
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                response = client.post(
                    f"/requests/{request_id}/cancel",
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}


class TestBookingOwnership:
    """Test booking ownership validation."""
    
    def test_user_cannot_access_other_user_booking(self, client, mock_user):
        """User should not be able to access another user's booking."""
        booking_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=False):
                mock_db = MagicMock()
                mock_booking = create_mock_booking(booking_id, OTHER_USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                response = client.get(
                    f"/bookings/{booking_id}",
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_consumer_can_access_own_booking(self, client, mock_user):
        """Consumer should be able to access their own booking."""
        booking_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=True):
                mock_db = MagicMock()
                mock_booking = create_mock_booking(booking_id, USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                response = client.get(
                    f"/bookings/{booking_id}",
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_200_OK
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_provider_can_access_own_booking(self, client, mock_user):
        """Provider should be able to access bookings for their services."""
        booking_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=True):
                mock_db = MagicMock()
                mock_booking = create_mock_booking(booking_id, OTHER_USER_ID, UUID(USER_ID))
                mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                response = client.get(
                    f"/bookings/{booking_id}",
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_200_OK
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_user_cannot_complete_other_user_booking(self, client, mock_user):
        """User should not be able to complete another user's booking."""
        booking_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            with patch('src.platform.auth.check_resource_ownership', return_value=False):
                mock_db = MagicMock()
                mock_booking = create_mock_booking(booking_id, OTHER_USER_ID)
                mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
                fastapi_app.dependency_overrides[get_db] = lambda: mock_db

                response = client.put(
                    f"/bookings/{booking_id}/complete",
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}


class TestOwnershipHelper:
    """Test the ownership helper functions."""
    
    def test_check_resource_ownership_provider(self):
        """Test provider ownership check."""
        from src.platform.auth import check_resource_ownership
        from unittest.mock import MagicMock
        
        mock_db = MagicMock()
        mock_provider = MagicMock()
        mock_provider.clerk_id = USER_ID
        mock_db.query.return_value.filter.return_value.first.return_value = mock_provider
        
        result = check_resource_ownership(
            "provider",
            uuid4(),
            USER_ID,
            mock_db
        )
        assert result is True
    
    def test_check_resource_ownership_request(self):
        """Test request ownership check."""
        from src.platform.auth import check_resource_ownership
        from unittest.mock import MagicMock
        
        mock_db = MagicMock()
        mock_request = MagicMock()
        mock_request.consumer_id = UUID(USER_ID)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_request
        
        result = check_resource_ownership(
            "request",
            uuid4(),
            USER_ID,
            mock_db
        )
        assert result is True
    
    def test_check_resource_ownership_admin_bypass(self):
        """Test admin bypass for ownership checks."""
        from src.platform.auth import check_resource_ownership
        from unittest.mock import MagicMock
        
        admin_user = {"public_metadata": {"role": "admin"}}
        mock_db = MagicMock()
        
        result = check_resource_ownership(
            "provider",
            uuid4(),
            ADMIN_ID,
            mock_db,
            admin_user
        )
        assert result is True
