"""
Rate limiting middleware for FastAPI.

Adds rate limit headers and enforces per-user rate limits.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import structlog
from src.platform.services.rate_limiter import rate_limiter_service
from src.platform.config import settings

logger = structlog.get_logger()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers and enforce limits."""
    
    # Default rate limits per endpoint
    DEFAULT_LIMITS = {
        "/chat": settings.RATE_LIMIT_CHAT_PER_MINUTE,
        "/requests": 60,
        "/offers": 30,
        "/bookings": 30,
        "/providers": 100,
        "/media/upload": 20,
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)
        
        # Determine endpoint and limit
        endpoint = self._get_endpoint(request.url.path)
        limit = self._get_limit_for_endpoint(endpoint)
        
        # Check rate limit
        is_allowed, rate_info = rate_limiter_service.check_rate_limit(
            request=request,
            endpoint=endpoint,
            limit=limit,
            window_seconds=60
        )
        
        # Add rate limit headers
        response = await call_next(request) if is_allowed else None
        
        if not is_allowed:
            # Rate limit exceeded
            logger.warning(
                "Rate limit exceeded",
                endpoint=endpoint,
                identifier=rate_limiter_service._get_identifier(request),
                limit=limit
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Maximum {limit} requests per minute.",
                    "rate_limit": rate_info
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["reset"] - int(time.time()))
                }
            )
        
        # Add rate limit headers to successful response
        if response:
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
        
        return response
    
    def _get_endpoint(self, path: str) -> str:
        """Extract endpoint identifier from path."""
        # Remove query params
        path = path.split("?")[0]
        
        # Normalize path
        if path.startswith("/"):
            path = path[1:]
        
        # Get first segment as endpoint
        parts = path.split("/")
        if parts:
            return f"/{parts[0]}"
        return path
    
    def _get_limit_for_endpoint(self, endpoint: str) -> int:
        """Get rate limit for endpoint."""
        return self.DEFAULT_LIMITS.get(endpoint, settings.RATE_LIMIT_PER_MINUTE)
