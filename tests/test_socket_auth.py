"""
Tests for WebSocket authentication.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.fixture
def mock_valid_token():
    """Mock valid JWT token."""
    return "valid.jwt.token"


@pytest.fixture
def mock_invalid_token():
    """Mock invalid JWT token."""
    return "invalid.token"


@pytest.fixture
def mock_decoded_token():
    """Mock decoded JWT token."""
    return {
        "sub": "user_123",
        "email": "user@example.com",
        "public_metadata": {"role": "consumer"}
    }


class TestSocketAuthentication:
    """Test Socket.io authentication."""
    
    @pytest.mark.asyncio
    async def test_connect_with_valid_token_in_auth(self, mock_valid_token, mock_decoded_token):
        """Connection should succeed with valid token in auth object."""
        from src.platform.socket_io import connect
        
        environ = {}
        auth = {"token": mock_valid_token}
        
        with patch('src.platform.socket_io.verify_token', return_value=mock_decoded_token):
            with patch('src.platform.socket_io.sio.save_session', new=AsyncMock()) as mock_save:
                result = await connect("test_sid", environ, auth)
                
                # Connection should be accepted
                assert result is True
                # Session should be saved with user info
                mock_save.assert_called_once()
                call_args = mock_save.call_args
                assert call_args[0][0] == "test_sid"
                assert call_args[0][1]["user_id"] == "user_123"
                assert call_args[0][1]["authenticated"] is True
    
    @pytest.mark.asyncio
    async def test_connect_with_token_in_query_string(self, mock_valid_token, mock_decoded_token):
        """Connection should succeed with token in query string."""
        from src.platform.socket_io import connect
        
        environ = {"QUERY_STRING": f"token={mock_valid_token}"}
        auth = None
        
        with patch('src.platform.socket_io.verify_token', return_value=mock_decoded_token):
            with patch('src.platform.socket_io.sio.save_session', new=AsyncMock()):
                result = await connect("test_sid", environ, auth)
                assert result is True
    
    @pytest.mark.asyncio
    async def test_connect_with_token_in_header(self, mock_valid_token, mock_decoded_token):
        """Connection should succeed with token in Authorization header."""
        from src.platform.socket_io import connect
        
        environ = {"HTTP_AUTHORIZATION": f"Bearer {mock_valid_token}"}
        auth = None
        
        with patch('src.platform.socket_io.verify_token', return_value=mock_decoded_token):
            with patch('src.platform.socket_io.sio.save_session', new=AsyncMock()):
                result = await connect("test_sid", environ, auth)
                assert result is True
    
    @pytest.mark.asyncio
    async def test_connect_without_token_rejected(self):
        """Connection should be rejected without token."""
        from src.platform.socket_io import connect
        
        environ = {}
        auth = None
        
        result = await connect("test_sid", environ, auth)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_connect_with_invalid_token_rejected(self, mock_invalid_token):
        """Connection should be rejected with invalid token."""
        from src.platform.socket_io import connect
        
        environ = {}
        auth = {"token": mock_invalid_token}
        
        with patch('src.platform.socket_io.verify_token', side_effect=Exception("Invalid token")):
            result = await connect("test_sid", environ, auth)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_join_session_requires_authentication(self):
        """join_session should require authentication."""
        from src.platform.socket_io import join_session
        
        # Mock session without authentication
        with patch('src.platform.socket_io.sio.get_session', new=AsyncMock(return_value={})):
            result = await join_session("test_sid", {"session_id": "test_session"})
            assert result["status"] == "error"
            assert "Authentication required" in result["message"]
    
    @pytest.mark.asyncio
    async def test_chat_message_requires_authentication(self):
        """chat_message should require authentication."""
        from src.platform.socket_io import chat_message
        from src.platform.socket_io import sio
        
        # Mock session without authentication
        with patch('src.platform.socket_io.sio.get_session', new=AsyncMock(return_value={})):
            with patch('src.platform.socket_io.sio.emit', new=AsyncMock()) as mock_emit:
                await chat_message("test_sid", {"content": "test"})
                
                # Should emit error message
                mock_emit.assert_called_once()
                call_args = mock_emit.call_args
                assert call_args[0][0] == "error"
                assert "Authentication required" in call_args[0][1]["message"]
    
    @pytest.mark.asyncio
    async def test_authenticated_user_can_join_session(self):
        """Authenticated user should be able to join session."""
        from src.platform.socket_io import join_session
        
        mock_session = {
            "user_id": "user_123",
            "authenticated": True
        }
        
        with patch('src.platform.socket_io.sio.get_session', new=AsyncMock(return_value=mock_session)):
            with patch('src.platform.socket_io.sio.enter_room', new=AsyncMock()):
                result = await join_session("test_sid", {"session_id": "test_session"})
                assert result["status"] == "ok"
