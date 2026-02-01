"""
Integration tests for async chat processing via Celery.
"""

import pytest
from uuid import uuid4
from fastapi import status
from unittest.mock import patch, AsyncMock, Mock
from fastapi.testclient import TestClient

from src.platform.worker import celery_app
from src.platform.config import settings


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "sub": "user_123",
        "email": "user@example.com",
        "public_metadata": {}
    }


@pytest.fixture
def auth_headers(mock_user):
    """Auth headers."""
    return {"Authorization": "Bearer valid_token"}


class TestAsyncChatProcessing:
    """Test async chat processing via Celery."""
    
    def test_chat_returns_task_id_in_async_mode(self, client: TestClient, auth_headers, mock_user):
        """Test that chat endpoint returns task_id when async mode is enabled."""
        with patch('src.platform.auth.get_optional_user', return_value=mock_user):
            with patch('src.platform.config.settings.FEATURE_ASYNC_CHAT_ENABLED', True):
                with patch('src.platform.config.settings.CELERY_TASK_ALWAYS_EAGER', False):
                    with patch('src.platform.worker.process_chat_message_task') as mock_task:
                        # Mock Celery task
                        mock_task_result = Mock()
                        mock_task_result.id = "test_task_123"
                        mock_task.delay.return_value = mock_task_result
                        
                        response = client.post(
                            "/chat/?async_mode=true",
                            json={
                                "message": "Hello",
                                "session_id": "test_session",
                                "role": "consumer"
                            },
                            headers=auth_headers
                        )
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert "task_id" in data
                        assert data["task_id"] == "test_task_123"
                        assert data["message"] == "Processing your message..."
    
    def test_chat_synchronous_when_async_disabled(self, client: TestClient, auth_headers, mock_user):
        """Test that chat processes synchronously when async mode is disabled."""
        with patch('src.platform.auth.get_optional_user', return_value=mock_user):
            with patch('src.platform.config.settings.FEATURE_ASYNC_CHAT_ENABLED', False):
                with patch('src.platform.services.chat.chat_service.handle_chat', new=AsyncMock(return_value=(
                    "session_123",
                    "Hello response",
                    None,
                    None,
                    False
                ))):
                    response = client.post(
                        "/chat/",
                        json={
                            "message": "Hello",
                            "session_id": "test_session",
                            "role": "consumer"
                        },
                        headers=auth_headers
                    )
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["task_id"] is None
                    assert data["message"] == "Hello response"
    
    def test_get_task_status_pending(self, client: TestClient, auth_headers, mock_user):
        """Test getting status of a pending task."""
        with patch('src.platform.auth.get_optional_user', return_value=mock_user):
            from celery.result import AsyncResult
            
            # Mock AsyncResult
            mock_result = Mock(spec=AsyncResult)
            mock_result.state = "PENDING"
            mock_result.ready.return_value = False
            
            with patch('src.platform.routers.chat.AsyncResult', return_value=mock_result):
                response = client.get(
                    "/chat/task/test_task_123",
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["task_id"] == "test_task_123"
                assert data["status"] == "PENDING"
                assert data["result"] is None
    
    def test_get_task_status_success(self, client: TestClient, auth_headers, mock_user):
        """Test getting status of a completed task."""
        with patch('src.platform.auth.get_optional_user', return_value=mock_user):
            from celery.result import AsyncResult
            
            # Mock AsyncResult
            mock_result = Mock(spec=AsyncResult)
            mock_result.state = "SUCCESS"
            mock_result.ready.return_value = True
            mock_result.successful.return_value = True
            mock_result.result = {
                "session_id": "session_123",
                "message": "Response message",
                "data": None,
                "draft": None,
                "awaiting_approval": False
            }
            
            with patch('src.platform.routers.chat.AsyncResult', return_value=mock_result):
                response = client.get(
                    "/chat/task/test_task_123",
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status"] == "SUCCESS"
                assert data["result"] is not None
                assert data["result"]["message"] == "Response message"
    
    def test_get_task_status_failure(self, client: TestClient, auth_headers, mock_user):
        """Test getting status of a failed task."""
        with patch('src.platform.auth.get_optional_user', return_value=mock_user):
            from celery.result import AsyncResult
            
            # Mock AsyncResult
            mock_result = Mock(spec=AsyncResult)
            mock_result.state = "FAILURE"
            mock_result.ready.return_value = True
            mock_result.successful.return_value = False
            mock_result.info = "Task failed: Error message"
            
            with patch('src.platform.routers.chat.AsyncResult', return_value=mock_result):
                response = client.get(
                    "/chat/task/test_task_123",
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status"] == "FAILURE"
                assert data["error"] == "Task failed: Error message"
    
    def test_celery_task_processes_chat(self):
        """Test that Celery task properly processes chat messages."""
        from src.platform.worker import process_chat_message_task
        
        # Mock chat service
        with patch('src.platform.services.chat.chat_service.handle_chat', new=AsyncMock(return_value=(
            "session_123",
            "Test response",
            {"test": "data"},
            None,
            False
        ))):
            # Mock asyncio.run to handle async function
            with patch('asyncio.run') as mock_run:
                mock_run.return_value = (
                    "session_123",
                    "Test response",
                    {"test": "data"},
                    None,
                    False
                )
                
                result = process_chat_message_task(
                    message="Test message",
                    session_id="session_123",
                    role="consumer"
                )
                
                assert result["status"] == "completed"
                assert result["session_id"] == "session_123"
                assert result["message"] == "Test response"
