"""
Integration tests for the complete Request → Matching → Offer → Booking flow.
"""

import pytest
from uuid import uuid4
from fastapi import status
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.platform.database import SessionLocal, Base, engine
from src.platform.models.provider import Provider
from src.platform.models.consumer import Consumer
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.models.booking import Booking
from src.platform.models.service import Service
from src.platform.auth import get_current_user
from src.platform.main import fastapi_app


@pytest.fixture
def consumer_user():
    """Mock consumer user."""
    uid = str(uuid4())
    return {
        "sub": uid,
        "email": f"consumer_{uid[:8]}@example.com",
        "public_metadata": {"role": "consumer"}
    }


@pytest.fixture
def provider_user():
    """Mock provider user."""
    uid = str(uuid4())
    return {
        "sub": uid,
        "email": f"provider_{uid[:8]}@example.com",
        "public_metadata": {"role": "provider"}
    }


@pytest.fixture
def consumer_auth_headers(consumer_user):
    """Auth headers for consumer."""
    return {"Authorization": "Bearer consumer_token"}


@pytest.fixture
def provider_auth_headers(provider_user):
    """Auth headers for provider."""
    return {"Authorization": "Bearer provider_token"}


@pytest.fixture
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()


@pytest.fixture
def test_provider(db_session, provider_user):
    """Create a test provider."""
    provider = Provider(
        id=uuid4(),
        clerk_id=provider_user["sub"],
        name="Test Provider",
        email=provider_user["email"],
        location={"city": "Brooklyn", "neighborhood": "Bed-Stuy"},
        specializations=["curly hair"],
        status="active",
        verified=True
    )
    db_session.add(provider)
    db_session.commit()
    db_session.refresh(provider)
    return provider


@pytest.fixture
def test_service(db_session, test_provider):
    """Create a test service for the provider."""
    service = Service(
        id=uuid4(),
        provider_id=test_provider.id,
        name="Haircut",
        category="hairstylist",
        description="Professional haircut",
        price_min=50,
        price_max=100,
        duration_minutes=60
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


@pytest.fixture
def test_consumer(db_session, consumer_user):
    """Create a test consumer."""
    consumer = Consumer(
        id=uuid4(),
        clerk_id=consumer_user["sub"],
        name="Test Consumer",
        email=consumer_user["email"]
    )
    db_session.add(consumer)
    db_session.commit()
    db_session.refresh(consumer)
    return consumer


class TestRequestToBookingFlow:
    """Test the complete request to booking flow."""
    
    @pytest.mark.asyncio
    async def test_full_request_to_booking_flow(
        self,
        client: TestClient,
        consumer_user,
        provider_user,
        consumer_auth_headers,
        provider_auth_headers,
        test_provider,
        test_service,
        test_consumer,
        db_session
    ):
        """
        Test the complete flow:
        1. Consumer creates request
        2. Provider sees lead
        3. Provider creates offer
        4. Consumer accepts offer
        5. Booking is created
        """
        # 1. Consumer creates request
        fastapi_app.dependency_overrides[get_current_user] = lambda: consumer_user
        
        try:
            with patch('src.platform.services.matching.MatchingService.find_providers', new=AsyncMock(return_value=[test_provider.id])):
                request_data = {
                    "consumer_id": str(test_consumer.clerk_id),
                    "raw_input": "I need a haircut for curly hair in Brooklyn",
                    "service_category": "hairstylist",
                    "service_type": "haircut",
                    "requirements": {
                        "description": "curly hair specialist",
                        "specializations": ["curly hair"]
                    },
                    "location": {
                        "city": "Brooklyn",
                        "neighborhood": "Bed-Stuy"
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
                
                request_response = client.post(
                    "/requests/",
                    json=request_data,
                    headers=consumer_auth_headers
                )
                
                assert request_response.status_code == status.HTTP_201_CREATED
                request_json = request_response.json()
                request_id = request_json["id"]
                
                # Verify request was created
                assert request_json["status"] == "matching"
                
            # 2. Provider sees the lead (list requests)
            fastapi_app.dependency_overrides[get_current_user] = lambda: provider_user
            leads_response = client.get(
                f"/requests/?matching_provider_id={test_provider.id}",
                headers=provider_auth_headers
            )
            
            assert leads_response.status_code == status.HTTP_200_OK
            leads = leads_response.json()
            assert len(leads) > 0
            assert any(lead["id"] == request_id for lead in leads)
            
            # 3. Provider creates offer
            offer_data = {
                "request_id": request_id,
                "provider_id": str(test_provider.id),
                "service_id": str(test_service.id),
                "service_name": "Haircut",
                "available_slots": [
                    {
                        "date": "2026-02-15",
                        "start_time": "14:00",
                        "end_time": "15:00"
                    }
                ],
                "price": 75.0,
                "currency": "USD",
                "price_notes": "Includes styling",
                "message": "I specialize in curly hair cuts!"
            }
            
            offer_response = client.post(
                "/offers/",
                json=offer_data,
                headers=provider_auth_headers
            )
            
            assert offer_response.status_code == status.HTTP_201_CREATED
            offer_json = offer_response.json()
            offer_id = offer_json["id"]
            
            # 4. Consumer accepts offer
            fastapi_app.dependency_overrides[get_current_user] = lambda: consumer_user
            accept_response = client.put(
                f"/offers/{offer_id}/accept",
                headers=consumer_auth_headers
            )
            
            assert accept_response.status_code == status.HTTP_200_OK
            booking_json = accept_response.json()
            booking_id = booking_json["id"]
            
            # 5. Get booking details
            booking_response = client.get(
                f"/bookings/{booking_id}",
                headers=consumer_auth_headers
            )
            
            assert booking_response.status_code == status.HTTP_200_OK
            assert booking_response.json()["id"] == booking_id
        finally:
            fastapi_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_provider_cannot_accept_own_offer(
        self,
        client: TestClient,
        provider_user,
        provider_auth_headers,
        test_provider,
        test_service,
        db_session
    ):
        """Provider should not be able to accept their own offer."""
        fastapi_app.dependency_overrides[get_current_user] = lambda: provider_user
        try:
            # Create a request directly in DB
            from uuid import uuid4
            request = ServiceRequest(
                id=uuid4(),
                consumer_id=str(uuid4()), # Different consumer
                raw_input="Test request",
                service_category="hairstylist",
                service_type="haircut",
                requirements={},
                location={"city": "Brooklyn"},
                timing={},
                budget={},
                status="matching"
            )
            db_session.add(request)
            db_session.commit()
            
            # Provider creates offer
            offer_data = {
                "request_id": str(request.id),
                "provider_id": str(test_provider.id),
                "service_id": str(test_service.id),
                "service_name": "Haircut",
                "available_slots": [{"date": "2026-02-15", "start_time": "14:00", "end_time": "15:00"}],
                "price": 75.0,
                "currency": "USD"
            }
            
            offer_response = client.post(
                "/offers/",
                json=offer_data,
                headers=provider_auth_headers
            )
            assert offer_response.status_code == status.HTTP_201_CREATED
            offer_id = offer_response.json()["id"]
            
            # Provider tries to accept their own offer (should fail because they are not the consumer)
            accept_response = client.put(
                f"/offers/{offer_id}/accept",
                headers=provider_auth_headers
            )
            # The error might be a 403 or 404 depending on ownership checks
            assert accept_response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        finally:
            fastapi_app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_consumer_cannot_create_offer(
        self,
        client: TestClient,
        consumer_user,
        consumer_auth_headers,
        test_consumer,
        db_session
    ):
        """Consumer should not be able to create offers."""
        fastapi_app.dependency_overrides[get_current_user] = lambda: consumer_user
        try:
            # Create a request
            request = ServiceRequest(
                id=uuid4(),
                consumer_id=test_consumer.clerk_id,
                raw_input="Test request",
                service_category="hairstylist",
                service_type="haircut",
                requirements={},
                location={"city": "Brooklyn"},
                timing={},
                budget={},
                status="matching"
            )
            db_session.add(request)
            db_session.commit()
            
            # Consumer tries to create offer
            offer_data = {
                "request_id": str(request.id),
                "provider_id": str(uuid4()),
                "service_id": str(uuid4()),
                "service_name": "Haircut",
                "available_slots": [],
                "price": 75.0,
                "currency": "USD"
            }
            
            offer_response = client.post(
                "/offers/",
                json=offer_data,
                headers=consumer_auth_headers
            )
            # Should fail with 403 (requires provider role)
            assert offer_response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            fastapi_app.dependency_overrides = {}
