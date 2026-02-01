"""
Proxie Cache Service - Request/Response Caching

Provides caching for API endpoints to reduce database load and improve response times.
"""

import json
import hashlib
import redis
import structlog
from typing import Optional, Any, Callable, Dict
from functools import wraps
from fastapi import Request, Response
from src.platform.config import settings

logger = structlog.get_logger()


class CacheService:
    """Service for managing API response caching."""
    
    def __init__(self):
        """Initialize cache service with Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_CACHE_DB,
                decode_responses=False  # Keep bytes for JSON
            )
            self.enabled = settings.LLM_CACHE_ENABLED  # Reuse LLM cache setting
        except Exception as e:
            logger.error("Failed to connect to Redis for caching", error=str(e))
            self.redis_client = None
            self.enabled = False
        
        self.default_ttl = 300  # 5 minutes default
    
    def _generate_cache_key(
        self,
        endpoint: str,
        params: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """Generate a deterministic cache key for an endpoint request."""
        # Normalize parameters (sort keys, handle None values)
        normalized_params = {}
        for k, v in sorted(params.items()):
            if v is not None:
                normalized_params[k] = v
        
        key_data = {
            "endpoint": endpoint,
            "params": normalized_params,
            "user_id": user_id
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        hash_val = hashlib.sha256(key_str.encode()).hexdigest()
        return f"api_cache:{endpoint}:{hash_val}"
    
    def get(self, key: str) -> Optional[bytes]:
        """Get cached value by key."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: bytes, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache keys matching a pattern."""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("Cache invalidation error", pattern=pattern, error=str(e))
            return 0
    
    def invalidate_endpoint(self, endpoint: str) -> int:
        """Invalidate all cache entries for an endpoint."""
        pattern = f"api_cache:{endpoint}:*"
        return self.invalidate_pattern(pattern)
    
    def invalidate_user(self, user_id: str) -> int:
        """Invalidate all cache entries for a user."""
        # This is less efficient - would need to scan keys
        # For now, we'll use a simpler approach with user-specific patterns
        pattern = f"api_cache:*:*{user_id}*"
        return self.invalidate_pattern(pattern)


# Global cache service instance
cache_service = CacheService()


def cached(
    ttl: int = 300,
    key_func: Optional[Callable] = None,
    invalidate_on: Optional[list] = None
):
    """
    Decorator to cache API endpoint responses.
    
    Args:
        ttl: Time to live in seconds (default: 300)
        key_func: Optional function to generate custom cache key
        invalidate_on: List of HTTP methods that invalidate cache (default: ['POST', 'PUT', 'PATCH', 'DELETE'])
    
    Usage:
        @router.get("/requests/")
        @cached(ttl=600)
        async def list_requests(...):
            ...
    """
    invalidate_on = invalidate_on or ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs (FastAPI dependency injection)
            request = None
            user_id = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            # Get user_id from request if available
            if request and hasattr(request.state, 'user'):
                user_id = request.state.user.get('sub')
            
            # Generate cache key
            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                # Default: use endpoint path + query params
                endpoint = request.url.path if request else func.__name__
                params = dict(request.query_params) if request else {}
                cache_key = cache_service._generate_cache_key(endpoint, params, user_id)
            
            # Check cache for GET requests
            if request and request.method == "GET":
                cached_value = cache_service.get(cache_key)
                if cached_value:
                    logger.info("Cache hit", endpoint=endpoint, key=cache_key[:50])
                    return Response(
                        content=cached_value,
                        media_type="application/json",
                        headers={"X-Cache": "HIT"}
                    )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache GET responses
            if request and request.method == "GET":
                if isinstance(result, Response):
                    # Already a Response object
                    response_content = result.body
                else:
                    # Convert to JSON
                    response_content = json.dumps(result).encode()
                
                cache_service.set(cache_key, response_content, ttl)
                logger.info("Cache set", endpoint=endpoint, key=cache_key[:50], ttl=ttl)
            
            # Invalidate cache on write operations
            if request and request.method in invalidate_on:
                endpoint = request.url.path if request else func.__name__
                cache_service.invalidate_endpoint(endpoint)
                logger.info("Cache invalidated", endpoint=endpoint)
            
            return result
        
        return wrapper
    return decorator
