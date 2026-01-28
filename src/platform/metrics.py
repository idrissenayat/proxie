"""
Custom Prometheus metrics for Proxie.
Tracks business-critical events and LLM usage for observability.
"""

from prometheus_client import Counter, Histogram, Gauge

# --- LLM Metrics ---
# Track token usage by model and provider
LLM_TOKENS_TOTAL = Counter(
    "proxie_llm_tokens_total",
    "Total tokens consumed by LLM components",
    ["provider", "model", "token_type"] # token_type: prompt, completion
)

# Track LLM latency
LLM_LATENCY_SECONDS = Histogram(
    "proxie_llm_latency_seconds",
    "Latency of LLM requests in seconds",
    ["provider", "model"]
)

# --- Business Metrics ---
# Track lifecycle of service requests
REQUESTS_CREATED_TOTAL = Counter(
    "proxie_requests_created_total",
    "Total service requests created by consumers",
    ["service_category"]
)

OFFERS_SUBMITTED_TOTAL = Counter(
    "proxie_offers_submitted_total",
    "Total offers submitted by providers",
    ["service_category"]
)

BOOKINGS_CONFIRMED_TOTAL = Counter(
    "proxie_bookings_confirmed_total",
    "Total bookings confirmed by consumers",
    ["service_category"]
)

# --- System Metrics ---
# Track active websocket connections
ACTIVE_WS_CONNECTIONS = Gauge(
    "proxie_active_ws_connections",
    "Number of active WebSocket connections"
)

def track_llm_usage(provider: str, model: str, prompt_tokens: int, completion_tokens: int):
    """Helper to record LLM token usage."""
    LLM_TOKENS_TOTAL.labels(provider=provider, model=model, token_type="prompt").inc(prompt_tokens)
    LLM_TOKENS_TOTAL.labels(provider=provider, model=model, token_type="completion").inc(completion_tokens)

def track_request_created(category: str):
    """Record a new service request."""
    REQUESTS_CREATED_TOTAL.labels(service_category=category).inc()

def track_offer_submitted(category: str):
    """Record a new offer."""
    OFFERS_SUBMITTED_TOTAL.labels(service_category=category).inc()

def track_booking_confirmed(category: str):
    """Record a confirmed booking."""
    BOOKINGS_CONFIRMED_TOTAL.labels(service_category=category).inc()
