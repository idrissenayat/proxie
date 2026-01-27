"""
Proxie API Server

Main entry point for the FastAPI application.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.platform.config import settings
from src.platform.database import engine, Base
# Import all models to ensure they are registered with Base
from src.platform.models.provider import Provider, ProviderLeadView
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.models.booking import Booking
from src.platform.models.review import Review

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Proxie API",
    description="Agent-native platform for skilled service providers",
    version="0.1.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Use configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.get("/")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def root(request: Request):
    """Health check endpoint."""
    return {
        "name": "Proxie API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def health(request: Request):
    """Detailed health check."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


# Import and include routers
from src.platform.routers import providers, requests, offers, bookings, reviews, mcp, chat, media, consumers, services, enrollment

app.include_router(providers.router)
app.include_router(requests.router)
app.include_router(offers.router)
app.include_router(bookings.router)
app.include_router(reviews.router)
app.include_router(mcp.router)
app.include_router(chat.router)
app.include_router(media.router)
app.include_router(consumers.router)
app.include_router(services.router)
app.include_router(enrollment.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

