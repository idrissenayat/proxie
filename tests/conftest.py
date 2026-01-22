"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from src.platform.main import app


@pytest.fixture
def client():
    """Test client for API testing."""
    return TestClient(app)


@pytest.fixture
def sample_provider():
    """Sample provider data for testing."""
    return {
        "name": "Test Provider",
        "email": "test@example.com",
        "bio": "Test bio",
        "location": {
            "city": "Brooklyn",
            "neighborhood": "Bed-Stuy"
        },
        "specializations": ["curly hair"],
    }


@pytest.fixture
def sample_request():
    """Sample service request for testing."""
    return {
        "raw_input": "I need a haircut for curly hair in Brooklyn this weekend",
        "service_category": "hairstylist",
        "service_type": "haircut",
        "requirements": {
            "specializations": ["curly hair"]
        },
        "location": {
            "city": "Brooklyn"
        },
        "timing": {
            "urgency": "specific_date"
        },
        "budget": {
            "min": 60,
            "max": 80,
            "currency": "USD"
        }
    }
