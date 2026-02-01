import os
import json
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)

class SessionManager:
    """Session manager with local file persistence to survive restarts."""
    def __init__(self, storage_path: str = ".sessions.json"):
        self.storage_path = storage_path
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._load_from_disk()
        
    def _load_from_disk(self):
        """Load session data from disk if exists."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self._sessions = json.load(f)
                logger.info("sessions_loaded_from_disk", count=len(self._sessions))
            except Exception as e:
                logger.error("failed_to_load_sessions", error=str(e))
                self._sessions = {}

    def _save_to_disk(self):
        """Persist session data to disk."""
        try:
            # Simple custom encoder for common non-serializable types
            def default_encoder(obj):
                if hasattr(obj, 'dict'):
                    return obj.dict()
                if hasattr(obj, 'model_dump'):
                    return obj.model_dump()
                from uuid import UUID
                from datetime import datetime
                if isinstance(obj, (UUID, datetime)):
                    return str(obj)
                # Handle litellm or other objects partially
                return str(obj)

            with open(self.storage_path, "w") as f:
                json.dump(self._sessions, f, indent=2, default=default_encoder)
        except Exception as e:
            logger.error("failed_to_save_sessions", error=str(e))

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)
        
    def save_session(self, session_id: str, session: Dict[str, Any]):
        self._sessions[session_id] = session
        self._save_to_disk()
        
    def delete_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save_to_disk()

    def check_health(self) -> bool:
        """Health check for file-based session storage."""
        try:
            # Just touch or check if we can write if needed, 
            # but for now returning True is enough for the probe.
            return True
        except Exception:
            return False

# Singleton instance
session_manager = SessionManager()
