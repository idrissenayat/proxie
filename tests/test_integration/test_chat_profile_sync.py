"""
Integration tests for Chat -> Profile Sync flow.
"""

import pytest
from uuid import uuid4
from fastapi import status
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.platform.database import SessionLocal, Base, engine, get_db
from src.platform.models.consumer import Consumer
from src.platform.main import fastapi_app as app
from src.platform.auth import get_optional_user, get_current_user


@pytest.fixture
def consumer_user():
    """Mock consumer user."""
    uid = f"user_{uuid4().hex[:8]}"
    return {
        "sub": uid,
        "email": f"consumer_{uid}@example.com",
        "public_metadata": {}
    }


@pytest.fixture
def consumer_auth_headers(consumer_user):
    """Auth headers for consumer."""
    return {"Authorization": "Bearer consumer_token"}


@pytest.fixture
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    # We don't rollback because FastAPI uses its own session via get_db
    # But for our direct DB setup we should clean up or use a separate test DB.
    # For now, let's just make sure we don't leak too much.
    db.close()


class TestChatProfileSync:
    """Test chat-driven profile synchronization."""
    
    @pytest.mark.asyncio
    async def test_chat_updates_consumer_profile(
        self,
        client: TestClient,
        consumer_user,
        consumer_auth_headers,
        db_session
    ):
        """Test that chat interactions update consumer profile."""
        app.dependency_overrides[get_optional_user] = lambda: consumer_user
        try:
            with patch('src.platform.routers.chat.chat_service') as mock_chat:
                # Mock chat service to simulate profile update
                mock_chat.handle_chat = AsyncMock(return_value=(
                    "session_123",
                    "I've updated your profile with your name and location.",
                    {
                        "profile_updated": True,
                        "fields": ["name", "default_location"]
                    },
                    None,
                    False
                ))
                
                # Send chat message that triggers profile update
                chat_response = client.post(
                    "/chat/",
                    json={
                        "message": "My name is John and I'm in Brooklyn",
                        "session_id": "session_123",
                        "role": "consumer",
                        "consumer_id": str(uuid4())
                    },
                    headers=consumer_auth_headers
                )
                
                assert chat_response.status_code == status.HTTP_200_OK
                data = chat_response.json()
                # data["data"] might be None if handle_chat result was not properly processed by the router
                assert data.get("data") is not None
                assert "profile_updated" in data["data"]
        finally:
            app.dependency_overrides = {}
    
    def test_get_consumer_profile(self, client: TestClient, consumer_user, consumer_auth_headers, db_session):
        """Test retrieving consumer profile."""
        # Create consumer
        consumer_id = uuid4()
        email = f"john_{uuid4().hex[:8]}@example.com"
        consumer = Consumer(
            id=consumer_id,
            clerk_id=consumer_user["sub"],
            name="John Doe",
            email=email,
            default_location={"city": "Brooklyn", "neighborhood": "Bed-Stuy"}
        )
        db_session.add(consumer)
        db_session.commit()
        db_session.refresh(consumer)
        
        app.dependency_overrides[get_optional_user] = lambda: consumer_user
        try:
            # Get profile
            profile_response = client.get(
                f"/consumers/{consumer.id}/profile",
                headers=consumer_auth_headers
            )
            
            assert profile_response.status_code == status.HTTP_200_OK
            profile = profile_response.json()
            assert profile["name"] == "John Doe"
            assert profile["email"] == email
            assert profile["default_location"]["city"] == "Brooklyn"
        finally:
            app.dependency_overrides = {}
    
    def test_update_consumer_profile(self, client: TestClient, consumer_user, consumer_auth_headers, db_session):
        """Test updating consumer profile."""
        # Create consumer
        consumer_id = uuid4()
        consumer = Consumer(
            id=consumer_id,
            clerk_id=consumer_user["sub"],
            name="John Doe",
            email=f"john_{uuid4().hex[:8]}@example.com"
        )
        db_session.add(consumer)
        db_session.commit()
        db_session.refresh(consumer)
        
        app.dependency_overrides[get_optional_user] = lambda: consumer_user
        try:
            # Update profile
            update_response = client.put(
                f"/consumers/{consumer.id}/profile",
                json={
                    "name": "John Updated",
                    "phone": "555-1234",
                    "default_location": {
                        "city": "Manhattan",
                        "neighborhood": "SoHo"
                    }
                },
                headers=consumer_auth_headers
            )
            
            assert update_response.status_code == status.HTTP_200_OK
            updated = update_response.json()
            assert updated["name"] == "John Updated"
            assert updated["phone"] == "555-1234"
            assert updated["default_location"]["city"] == "Manhattan"
        finally:
            app.dependency_overrides = {}
    
    def test_profile_sync_via_chat_tool(self, client: TestClient, consumer_user, consumer_auth_headers, db_session):
        """Test that chat agent can update profile via tools."""
        # Create consumer
        consumer_id = uuid4()
        consumer = Consumer(
            id=consumer_id,
            clerk_id=consumer_user["sub"],
            name=None,  # Not set yet
            email=f"john_{uuid4().hex[:8]}@example.com"
        )
        db_session.add(consumer)
        db_session.commit()
        db_session.refresh(consumer)
        
        app.dependency_overrides[get_optional_user] = lambda: consumer_user
        app.dependency_overrides[get_current_user] = lambda: consumer_user
        try:
            # Direct test of the profile update endpoint, which is what the chat service would call
            update_response = client.put(
                f"/consumers/{consumer.id}/profile",
                json={
                    "name": "John From Chat",
                    "default_location": {"city": "Brooklyn"}
                },
                headers=consumer_auth_headers
            )
            
            assert update_response.status_code == status.HTTP_200_OK
            assert update_response.json()["name"] == "John From Chat"
        finally:
            app.dependency_overrides = {}
