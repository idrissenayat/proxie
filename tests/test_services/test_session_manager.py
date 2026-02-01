"""
Unit tests for SessionManager (file-based) and Redis session management.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from src.platform.services.session_manager import SessionManager


@pytest.fixture
def temp_storage_path():
    """Create a temporary file path for session storage."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def session_manager(temp_storage_path):
    """Create SessionManager instance with temp storage."""
    return SessionManager(storage_path=temp_storage_path)


class TestSessionManager:
    """Test SessionManager functionality."""
    
    def test_initialization(self, session_manager):
        """Test SessionManager initialization."""
        assert session_manager.storage_path is not None
        assert isinstance(session_manager._sessions, dict)
    
    def test_save_and_get_session(self, session_manager):
        """Test saving and retrieving a session."""
        session_id = str(uuid4())
        session_data = {
            "user_id": "user_123",
            "role": "consumer",
            "messages": []
        }
        
        session_manager.save_session(session_id, session_data)
        retrieved = session_manager.get_session(session_id)
        
        assert retrieved is not None
        assert retrieved["user_id"] == "user_123"
        assert retrieved["role"] == "consumer"
    
    def test_get_nonexistent_session(self, session_manager):
        """Test retrieving a non-existent session."""
        result = session_manager.get_session("nonexistent_id")
        assert result is None
    
    def test_delete_session(self, session_manager):
        """Test deleting a session."""
        session_id = str(uuid4())
        session_data = {"test": "data"}
        
        session_manager.save_session(session_id, session_data)
        assert session_manager.get_session(session_id) is not None
        
        session_manager.delete_session(session_id)
        assert session_manager.get_session(session_id) is None
    
    def test_persistence_to_disk(self, session_manager, temp_storage_path):
        """Test that sessions are persisted to disk."""
        session_id = str(uuid4())
        session_data = {"test": "persistence"}
        
        session_manager.save_session(session_id, session_data)
        
        # Verify file exists
        assert os.path.exists(temp_storage_path)
        
        # Verify file contents
        with open(temp_storage_path, 'r') as f:
            data = json.load(f)
            assert session_id in data
            assert data[session_id]["test"] == "persistence"
    
    def test_load_from_disk(self, temp_storage_path):
        """Test loading sessions from disk."""
        # Create a session file manually
        session_id = str(uuid4())
        session_data = {"loaded": "from_disk"}
        
        with open(temp_storage_path, 'w') as f:
            json.dump({session_id: session_data}, f)
        
        # Create new manager - should load from disk
        manager = SessionManager(storage_path=temp_storage_path)
        retrieved = manager.get_session(session_id)
        
        assert retrieved is not None
        assert retrieved["loaded"] == "from_disk"
    
    def test_load_from_nonexistent_file(self):
        """Test loading when file doesn't exist."""
        manager = SessionManager(storage_path="/nonexistent/path/sessions.json")
        assert isinstance(manager._sessions, dict)
        assert len(manager._sessions) == 0
    
    def test_load_corrupted_file(self, temp_storage_path):
        """Test handling of corrupted session file."""
        # Write invalid JSON
        with open(temp_storage_path, 'w') as f:
            f.write("invalid json {")
        
        # Should handle gracefully
        manager = SessionManager(storage_path=temp_storage_path)
        assert isinstance(manager._sessions, dict)
        assert len(manager._sessions) == 0
    
    def test_save_with_uuid(self, session_manager):
        """Test saving session with UUID objects."""
        from uuid import UUID
        
        session_id = str(uuid4())
        session_data = {
            "id": UUID(session_id),
            "name": "Test"
        }
        
        # Should handle UUID serialization
        session_manager.save_session(session_id, session_data)
        retrieved = session_manager.get_session(session_id)
        
        assert retrieved is not None
        # UUID should be converted to string
        assert isinstance(retrieved["id"], str) or isinstance(retrieved["id"], UUID)
    
    def test_multiple_sessions(self, session_manager):
        """Test managing multiple sessions."""
        session1_id = str(uuid4())
        session2_id = str(uuid4())
        
        session_manager.save_session(session1_id, {"data": "1"})
        session_manager.save_session(session2_id, {"data": "2"})
        
        assert session_manager.get_session(session1_id)["data"] == "1"
        assert session_manager.get_session(session2_id)["data"] == "2"
    
    def test_update_existing_session(self, session_manager):
        """Test updating an existing session."""
        session_id = str(uuid4())
        
        session_manager.save_session(session_id, {"count": 1})
        session_manager.save_session(session_id, {"count": 2})
        
        retrieved = session_manager.get_session(session_id)
        assert retrieved["count"] == 2


class TestRedisSessionManager:
    """Test Redis-based session management (if used)."""
    
    @pytest.mark.asyncio
    async def test_redis_session_health_check(self):
        """Test Redis session manager health check."""
        # This would test the Redis session manager from sessions.py
        # For now, we'll skip if Redis isn't available
        try:
            from src.platform.sessions import session_manager
            health = session_manager.check_health()
            assert isinstance(health, bool)
        except ImportError:
            pytest.skip("Redis session manager not available")
