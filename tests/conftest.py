"""
Pytest configuration and fixtures.
"""

import pytest
import os

# Set environment to testing for all tests (matches auth bypass)
os.environ["ENVIRONMENT"] = "testing"
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "True" # Ensure tasks run immediately in tests

from fastapi.testclient import TestClient

from src.platform.main import app
from src.platform.config import settings


@pytest.fixture
def client():
    """Test client for API testing."""
    return TestClient(app)


@pytest.fixture
def authed_client():
    """Test client that bypasses authentication."""
    c = TestClient(app)
    c.headers.update({
        "X-Load-Test-Secret": settings.LOAD_TEST_SECRET,
        "X-Test-User-Id": "550e8400-e29b-41d4-a716-446655440000",
        "X-Test-User-Role": "consumer"
    })
    return c


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
