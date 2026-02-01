"""
Proxie API Server

Main entry point for the FastAPI application.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.platform.services.rate_limiter import get_user_id_for_rate_limit
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.platform.config import settings
from src.platform.log_config import setup_logging
import structlog
from src.platform.database import engine, Base
# Import all models to ensure they are registered with Base
from src.platform.models.provider import Provider, ProviderLeadView
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.models.booking import Booking
from src.platform.models.review import Review
from src.platform.models.consumer import Consumer
from src.platform.models.usage import LLMUsage

# Setup Logging
setup_logging()
logger = structlog.get_logger()

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
    )

# Setup OpenTelemetry
if settings.ENVIRONMENT not in ["test", "testing"]:
    resource = Resource(attributes={SERVICE_NAME: "proxie-api"})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter with user-based key function
limiter = Limiter(key_func=get_user_id_for_rate_limit)

fastapi_app = FastAPI(
    title="Proxie API",
    description="""
# Proxie API Documentation

Agent-native platform connecting skilled service providers with consumers through AI-powered matching and communication.

## Features

* **AI-First Concierge**: Conversational request creation with natural language processing
* **Smart Matching**: Automated provider discovery using semantic search and embeddings
* **Real-time Communication**: WebSocket-based chat for instant messaging
* **Provider Enrollment**: Streamlined onboarding process for new providers
* **Booking Management**: End-to-end booking workflow from request to completion
* **Review System**: Rating and review system for quality assurance

## Authentication

Proxie uses **Clerk** for authentication. Include a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### User Roles

- **consumer**: Service requesters
- **provider**: Service providers
- **admin**: Platform administrators

## Rate Limiting

Rate limits are enforced per user (authenticated) or per IP (unauthenticated). Rate limit headers are included in all responses:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

When rate limit is exceeded, a `429 Too Many Requests` response is returned with a `Retry-After` header.

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message",
  "rate_limit": {
    "limit": 60,
    "remaining": 0,
    "reset": 1706457600
  }
}
```

## Base URL

- **Production**: `https://api.proxie.app`
- **Development**: `http://localhost:8000`

## OpenAPI Specification

This API follows the OpenAPI 3.0 specification. The full schema is available at `/openapi.json`.
""",
    version="0.12.0",
    terms_of_service="https://proxie.app/terms/",
    contact={
        "name": "Proxie Support",
        "url": "https://proxie.app/support",
        "email": "support@proxie.app",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://proxie.app/license",
    },
    openapi_tags=[
        {
            "name": "requests",
            "description": "Service request management. Consumers create requests, providers view and respond to them.",
        },
        {
            "name": "providers",
            "description": "Provider profile and service management. Providers can manage their profile, services, and portfolio.",
        },
        {
            "name": "offers",
            "description": "Offer management. Providers create offers in response to requests, consumers accept them.",
        },
        {
            "name": "bookings",
            "description": "Booking management. Track and manage confirmed appointments.",
        },
        {
            "name": "reviews",
            "description": "Review and rating system. Consumers can leave reviews after completed bookings.",
        },
        {
            "name": "chat",
            "description": "AI-powered chat interface. Conversational interaction with Proxie AI agents.",
        },
        {
            "name": "enrollment",
            "description": "Provider enrollment process. New providers can sign up and get verified.",
        },
        {
            "name": "consumers",
            "description": "Consumer profile management.",
        },
        {
            "name": "media",
            "description": "Media upload and management. Upload photos and files for requests and portfolios.",
        },
    ],
)

# Add rate limiter to fastapi_app state
fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Instrument FastAPI with OpenTelemetry
if settings.ENVIRONMENT not in ["test", "testing"]:
    FastAPIInstrumentor.instrument_app(fastapi_app)

# Instrument with Prometheus metrics
Instrumentator().instrument(fastapi_app).expose(fastapi_app)

# CORS middleware - Use configured origins
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Load-Test-Secret", "X-Test-User-Id", "X-Test-User-Role"],
)


# Rate limiting middleware (if enabled)
if settings.RATE_LIMIT_ENABLED:
    from src.platform.middleware.rate_limit import RateLimitMiddleware
    fastapi_app.add_middleware(RateLimitMiddleware)

# Security headers middleware
@fastapi_app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Skip for WebSocket requests as it can cause issues with Starlette's BaseHTTPMiddleware
    if request.scope.get("type") == "websocket":
        return await call_next(request)
        
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@fastapi_app.get("/")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def root(request: Request):
    """Health check endpoint."""
    return {
        "name": "Proxie API",
        "version": "0.1.0",
        "status": "running",
    }


@fastapi_app.get("/health")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def health(request: Request):
    """Liveness probe."""
    return {
        "status": "healthy",
        "timestamp": structlog.processors.TimeStamper(fmt="iso")(None, None, {})["timestamp"],
        "version": fastapi_app.version,
    }


@fastapi_app.get("/ready")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def ready(request: Request):
    """Readiness probe."""
    from src.platform.database import check_db_connection
    from src.platform.sessions import session_manager
    
    db_up = check_db_connection()
    redis_up = session_manager.check_health()
    
    if not db_up or not redis_up:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "checks": {
                    "database": "up" if db_up else "down",
                    "redis": "up" if redis_up else "down",
                }
            }
        )
        
    return {
        "status": "ready",
        "checks": {
            "database": "up",
            "redis": "up",
        }
    }


# Import and include routers
from src.platform.routers import providers, requests, offers, bookings, reviews, mcp, chat, media, consumers, services, enrollment

fastapi_app.include_router(providers.router)
fastapi_app.include_router(requests.router)
fastapi_app.include_router(offers.router)
fastapi_app.include_router(bookings.router)
fastapi_app.include_router(reviews.router)
fastapi_app.include_router(mcp.router)
fastapi_app.include_router(chat.router)
fastapi_app.include_router(media.router)
fastapi_app.include_router(consumers.router)
fastapi_app.include_router(services.router)
fastapi_app.include_router(enrollment.router)

# Import Socket.io
from src.platform.socket_io import create_socket_app

# Wrap app with Socket.io at the very end
# This handles /ws/socket.io at the root level before hitting FastAPI
# IMPORTANT: No more FastAPI-specific calls (like include_router) can be made on 'fastapi_app' after this
app = create_socket_app(fastapi_app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

