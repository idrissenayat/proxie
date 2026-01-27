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
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
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
resource = Resource(attributes={SERVICE_NAME: "proxie-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Proxie API",
    description="Agent-native platform for skilled service providers",
    version="0.12.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

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
    """Liveness probe."""
    return {
        "status": "healthy",
        "timestamp": structlog.processors.TimeStamper(fmt="iso")(None, None, {})["timestamp"],
        "version": app.version,
    }


@app.get("/ready")
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

# Import Socket.io
from src.platform.socket_io import create_socket_app

# Wrap app with Socket.io at the very end
# This handles /ws/socket.io at the root level before hitting FastAPI
# IMPORTANT: No more FastAPI-specific calls (like include_router) can be made on 'app' after this
app = create_socket_app(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

