"""
Per-user rate limiting service using Redis.

Provides rate limiting based on user ID (from JWT) with fallback to IP address.
"""

import time
import redis
import structlog
from typing import Optional
from fastapi import Request, HTTPException, status
from slowapi.util import get_remote_address
from src.platform.config import settings
from src.platform.auth import verify_token

logger = structlog.get_logger()


class RateLimiterService:
    """Service for per-user rate limiting using Redis."""
    
    def __init__(self):
        """Initialize rate limiter with Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_CACHE_DB,
                decode_responses=False
            )
            self.enabled = True
        except Exception as e:
            logger.error("Failed to connect to Redis for rate limiting", error=str(e))
            self.redis_client = None
            self.enabled = False
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token in request."""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split()[1]
                decoded = verify_token(token)
                return decoded.get("sub")
            except Exception as e:
                logger.debug("Failed to extract user ID from token", error=str(e))
        return None
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get identifier for rate limiting.
        Prefers user ID, falls back to IP address.
        """
        user_id = self._get_user_id(request)
        if user_id:
            return f"user:{user_id}"
        return f"ip:{get_remote_address(request)}"
    
    def _get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Generate Redis key for rate limit tracking."""
        return f"rate_limit:{endpoint}:{identifier}"
    
    def check_rate_limit(
        self,
        request: Request,
        endpoint: str,
        limit: int,
        window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit.
        
        Args:
            request: FastAPI request object
            endpoint: Endpoint identifier (e.g., "/chat")
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
            rate_limit_info contains:
                - limit: Maximum requests
                - remaining: Remaining requests
                - reset: Unix timestamp when limit resets
        """
        if not self.enabled or not self.redis_client:
            # If Redis is unavailable, allow all requests
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time()) + window_seconds
            }
        
        identifier = self._get_identifier(request)
        key = self._get_rate_limit_key(identifier, endpoint)
        
        try:
            # Use sliding window log algorithm
            now = time.time()
            window_start = now - window_seconds
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_count = self.redis_client.zcard(key)
            
            if current_count >= limit:
                # Rate limit exceeded
                # Get oldest entry to calculate reset time
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                reset_time = int(oldest[0][1] + window_seconds) if oldest else int(now + window_seconds)
                
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset": reset_time
                }
            
            # Add current request
            self.redis_client.zadd(key, {str(now): now})
            self.redis_client.expire(key, window_seconds)
            
            remaining = limit - current_count - 1
            reset_time = int(now + window_seconds)
            
            return True, {
                "limit": limit,
                "remaining": max(0, remaining),
                "reset": reset_time
            }
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e), endpoint=endpoint)
            # On error, allow request but log it
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time()) + window_seconds
            }
    
    def get_rate_limit_info(
        self,
        request: Request,
        endpoint: str,
        limit: int,
        window_seconds: int = 60
    ) -> dict:
        """Get current rate limit status without incrementing counter."""
        if not self.enabled or not self.redis_client:
            return {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time()) + window_seconds
            }
        
        identifier = self._get_identifier(request)
        key = self._get_rate_limit_key(identifier, endpoint)
        
        try:
            now = time.time()
            window_start = now - window_seconds
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = self.redis_client.zcard(key)
            remaining = max(0, limit - current_count)
            
            # Get reset time
            oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1] + window_seconds) if oldest else int(now + window_seconds)
            
            return {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time
            }
        except Exception as e:
            logger.error("Rate limit info check failed", error=str(e))
            return {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time()) + window_seconds
            }


# Global rate limiter instance
rate_limiter_service = RateLimiterService()


def get_user_id_for_rate_limit(request: Request) -> str:
    """
    Key function for slowapi Limiter.
    Returns user ID if authenticated, otherwise IP address.
    """
    user_id = rate_limiter_service._get_user_id(request)
    if user_id:
        return f"user:{user_id}"
    return get_remote_address(request)
