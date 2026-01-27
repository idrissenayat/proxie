import json
from typing import Any, Dict, Optional
import redis
import structlog
from src.platform.config import settings

logger = structlog.get_logger()

class SessionManager:
    """Manages user sessions using Redis."""
    
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_SESSION_DB,
            decode_responses=True
        )
        self.prefix = "session:"
        self.ttl = 86400  # 24 hours
        
    def _key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from Redis."""
        try:
            data = self.redis.get(self._key(session_id))
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("redis_session_get_error", error=str(e), session_id=session_id)
            return None
            
    def save_session(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None):
        """Save or update session data in Redis."""
        try:
            self.redis.set(
                self._key(session_id),
                json.dumps(data),
                ex=ttl or self.ttl
            )
        except Exception as e:
            logger.error("redis_session_save_error", error=str(e), session_id=session_id)
            
    def delete_session(self, session_id: str):
        """Remove session from Redis."""
        try:
            self.redis.delete(self._key(session_id))
        except Exception as e:
            logger.error("redis_session_delete_error", error=str(e), session_id=session_id)

    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Perform a partial update on a session."""
        session = self.get_session(session_id) or {}
        session.update(updates)
        self.save_session(session_id, session)

    def check_health(self) -> bool:
        """Check if Redis is reachable."""
        try:
            return self.redis.ping()
        except Exception as e:
            logger.error("redis_health_check_failed", error=str(e))
            return False

# Global instance
session_manager = SessionManager()
