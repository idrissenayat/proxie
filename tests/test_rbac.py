"""
Tests for Role-Based Access Control (RBAC).
"""

import pytest
from uuid import uuid4
from fastapi import status
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from src.platform.auth import get_current_user
from src.platform.main import fastapi_app


@pytest.fixture
def mock_consumer_user():
    """Mock authenticated consumer user."""
    return {
        "sub": "consumer_123",
        "email": "consumer@example.com",
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
def mock_user_no_role():
    """Mock authenticated user without role."""
    return {
        "sub": "user_123",
        "email": "user@example.com",
        "public_metadata": {}
    }


class TestProviderRoleRequired:
    """Test that provider-only endpoints require provider role."""
    
    def test_create_service_requires_provider_role(self, client, mock_consumer_user):
        """POST /providers/{id}/services should reject consumer users."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_consumer_user
        try:
            # Mock database to return no provider/consumer records
            with patch('src.platform.auth.get_user_role_from_db', return_value="consumer"):
                response = client.post(
                    f"/providers/{provider_id}/services",
                    json={
                        "service_name": "Haircut",
                        "price": 50
                    },
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
                assert "provider" in response.json()["detail"].lower()
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_add_portfolio_requires_provider_role(self, client, mock_consumer_user):
        """POST /providers/{id}/portfolio should reject consumer users."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_consumer_user
        try:
            with patch('src.platform.auth.get_user_role_from_db', return_value="consumer"):
                response = client.post(
                    f"/providers/{provider_id}/portfolio",
                    json={
                        "photo_url": "https://example.com/photo.jpg",
                        "caption": "Test"
                    },
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_provider_endpoints_allow_provider_role(self, client, mock_provider_user):
        """Provider endpoints should allow users with provider role."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_provider_user
        try:
            with patch('src.platform.auth.get_user_role_from_db', return_value="provider"):
                response = client.post(
                    f"/providers/{provider_id}/services",
                    json={"service_name": "Haircut", "price": 50},
                    headers={"Authorization": "Bearer mock_token"}
                )
                # Should not return 403 (might return 404 if provider not found, which is OK)
                assert response.status_code != status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}


class TestConsumerRoleRequired:
    """Test that consumer-only endpoints require consumer role."""
    
    def test_create_request_requires_consumer_role(self, client, mock_provider_user):
        """POST /requests should reject provider users."""
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_provider_user
        try:
            with patch('src.platform.auth.get_user_role_from_db', return_value="provider"):
                response = client.post(
                    "/requests",
                    json={
                        "raw_input": "I need a haircut",
                        "service_category": "hairstylist",
                        "service_type": "haircut",
                        "consumer_id": str(uuid4()),
                        "requirements": {},
                        "location": {},
                        "timing": {},
                        "budget": {}
                    },
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
                assert "consumer" in response.json()["detail"].lower()
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_accept_offer_requires_consumer_role(self, client, mock_provider_user):
        """PUT /offers/{id}/accept should reject provider users."""
        offer_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_provider_user
        try:
            with patch('src.platform.auth.get_user_role_from_db', return_value="provider"):
                response = client.put(
                    f"/offers/{offer_id}/accept",
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_consumer_endpoints_allow_consumer_role(self, client, mock_consumer_user):
        """Consumer endpoints should allow users with consumer role."""
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_consumer_user
        try:
            with patch('src.platform.auth.get_user_role_from_db', return_value="consumer"):
                response = client.post(
                    "/requests",
                    json={
                        "raw_input": "I need a haircut",
                        "service_category": "hairstylist",
                        "service_type": "haircut",
                        "consumer_id": mock_consumer_user["sub"],
                        "requirements": {},
                        "location": {},
                        "timing": {},
                        "budget": {}
                    },
                    headers={"Authorization": "Bearer mock_token"}
                )
                # Should not return 403 (might return validation errors, which is OK)
                assert response.status_code != status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}


class TestRoleFromDatabase:
    """Test that roles are correctly determined from database records."""
    
    def test_role_determined_from_provider_record(self, client, mock_user_no_role):
        """User with Provider record should be treated as provider."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user_no_role
        try:
            # Mock database to return provider record
            with patch('src.platform.auth.get_user_role_from_db', return_value="provider"):
                response = client.post(
                    f"/providers/{provider_id}/services",
                    json={"service_name": "Haircut", "price": 50},
                    headers={"Authorization": "Bearer mock_token"}
                )
                # Should not return 403 (role determined from DB)
                assert response.status_code != status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_role_determined_from_consumer_record(self, client, mock_user_no_role):
        """User with Consumer record should be treated as consumer."""
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user_no_role
        try:
            # Mock database to return consumer record
            with patch('src.platform.auth.get_user_role_from_db', return_value="consumer"):
                response = client.post(
                    "/requests",
                    json={
                        "raw_input": "I need a haircut",
                        "service_category": "hairstylist",
                        "service_type": "haircut",
                        "consumer_id": mock_user_no_role["sub"],
                        "requirements": {},
                        "location": {},
                        "timing": {},
                        "budget": {}
                    },
                    headers={"Authorization": "Bearer mock_token"}
                )
                # Should not return 403 (role determined from DB)
                assert response.status_code != status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_no_role_returns_403(self, client, mock_user_no_role):
        """User with no role in metadata or DB should be rejected."""
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: mock_user_no_role
        try:
            # Mock database to return no role
            with patch('src.platform.auth.get_user_role_from_db', return_value=None):
                response = client.post(
                    f"/providers/{provider_id}/services",
                    json={"service_name": "Haircut", "price": 50},
                    headers={"Authorization": "Bearer mock_token"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}


class TestAdminRole:
    """Test that admin role can access any endpoint."""
    
    def test_admin_can_access_provider_endpoints(self, client):
        """Admin should be able to access provider endpoints."""
        admin_user = {
            "sub": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        provider_id = uuid4()
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: admin_user
        try:
            response = client.post(
                f"/providers/{provider_id}/services",
                json={"service_name": "Haircut", "price": 50},
                headers={"Authorization": "Bearer mock_token"}
            )
            # Admin should not get 403
            assert response.status_code != status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
    
    def test_admin_can_access_consumer_endpoints(self, client):
        """Admin should be able to access consumer endpoints."""
        admin_user = {
            "sub": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        
        fastapi_app.dependency_overrides[get_current_user] = lambda: admin_user
        try:
            response = client.post(
                "/requests",
                json={
                    "raw_input": "I need a haircut",
                    "service_category": "hairstylist",
                    "service_type": "haircut",
                    "consumer_id": admin_user["sub"],
                    "requirements": {},
                    "location": {},
                    "timing": {},
                    "budget": {}
                },
                headers={"Authorization": "Bearer mock_token"}
            )
            # Admin should not get 403
            assert response.status_code != status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
