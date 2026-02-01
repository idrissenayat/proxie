"""Tests for database models."""

import pytest


def test_provider_model():
    """Test Provider model creation."""
    from src.platform.models import Provider
    
    provider = Provider(
        name="Test Provider",
        email="test@example.com",
        status="active"  # Explicitly set for in-memory test
    )
    
    assert provider.name == "Test Provider"
    assert provider.email == "test@example.com"
    assert provider.status == "active"


def test_service_request_model():
    """Test ServiceRequest model creation."""
    from src.platform.models import ServiceRequest
    
    request = ServiceRequest(
        raw_input="I need a haircut",
        service_category="hairstylist",
        status="pending"  # Explicitly set for in-memory test
    )
    
    assert request.service_category == "hairstylist"
    assert request.status == "pending"
