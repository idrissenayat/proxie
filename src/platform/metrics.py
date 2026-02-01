"""
Custom Prometheus metrics for Proxie.
Tracks business-critical events and LLM usage for observability.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary

# --- LLM Metrics ---
# Track token usage by model and provider
LLM_TOKENS_TOTAL = Counter(
    "proxie_llm_tokens_total",
    "Total tokens consumed by LLM components",
    ["provider", "model", "token_type"]  # token_type: prompt, completion
)

# Track LLM latency
LLM_LATENCY_SECONDS = Histogram(
    "proxie_llm_latency_seconds",
    "Latency of LLM requests in seconds",
    ["provider", "model"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

# Track LLM request outcomes
LLM_REQUESTS_TOTAL = Counter(
    "proxie_llm_requests_total",
    "Total LLM requests by outcome",
    ["provider", "model", "status"]  # status: success, error, fallback
)

# Track LLM cost in cents
LLM_COST_CENTS = Counter(
    "proxie_llm_cost_cents",
    "Estimated LLM cost in cents",
    ["provider", "model"]
)

# --- Cache Metrics ---
CACHE_OPERATIONS_TOTAL = Counter(
    "proxie_cache_operations_total",
    "Total cache operations",
    ["cache_type", "operation", "result"]  # cache_type: llm, session; operation: get, set; result: hit, miss, error
)

CACHE_LATENCY_SECONDS = Histogram(
    "proxie_cache_latency_seconds",
    "Cache operation latency in seconds",
    ["cache_type", "operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25]
)

CACHE_SIZE_BYTES = Gauge(
    "proxie_cache_size_bytes",
    "Estimated cache size in bytes",
    ["cache_type"]
)

# --- Database Metrics ---
DB_QUERY_LATENCY_SECONDS = Histogram(
    "proxie_db_query_latency_seconds",
    "Database query latency in seconds",
    ["operation", "table"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

DB_CONNECTIONS_ACTIVE = Gauge(
    "proxie_db_connections_active",
    "Number of active database connections"
)

DB_QUERY_ERRORS_TOTAL = Counter(
    "proxie_db_query_errors_total",
    "Total database query errors",
    ["operation", "error_type"]
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


# --- Cache Tracking Helpers ---
def track_cache_hit(cache_type: str, operation: str = "get"):
    """Record a cache hit."""
    CACHE_OPERATIONS_TOTAL.labels(cache_type=cache_type, operation=operation, result="hit").inc()


def track_cache_miss(cache_type: str, operation: str = "get"):
    """Record a cache miss."""
    CACHE_OPERATIONS_TOTAL.labels(cache_type=cache_type, operation=operation, result="miss").inc()


def track_cache_error(cache_type: str, operation: str):
    """Record a cache error."""
    CACHE_OPERATIONS_TOTAL.labels(cache_type=cache_type, operation=operation, result="error").inc()


def track_cache_set(cache_type: str):
    """Record a cache set operation."""
    CACHE_OPERATIONS_TOTAL.labels(cache_type=cache_type, operation="set", result="success").inc()


# --- LLM Extended Tracking ---
def track_llm_request(provider: str, model: str, status: str):
    """Track LLM request outcome."""
    LLM_REQUESTS_TOTAL.labels(provider=provider, model=model, status=status).inc()


def track_llm_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int):
    """
    Track estimated LLM cost in cents.

    Pricing (per 1M tokens):
    - Gemini 2.0 Flash: $0.10 input / $0.40 output
    - Claude 3.5 Sonnet: $3.00 input / $15.00 output
    """
    pricing = {
        "gemini": {"input": 0.10, "output": 0.40},
        "anthropic": {"input": 3.00, "output": 15.00},
    }

    rates = pricing.get(provider.lower(), {"input": 1.0, "output": 1.0})
    cost_cents = (
        (prompt_tokens / 1_000_000 * rates["input"] * 100) +
        (completion_tokens / 1_000_000 * rates["output"] * 100)
    )
    LLM_COST_CENTS.labels(provider=provider, model=model).inc(cost_cents)


# --- Database Tracking Helpers ---
def track_db_query(operation: str, table: str, latency: float):
    """Track database query latency."""
    DB_QUERY_LATENCY_SECONDS.labels(operation=operation, table=table).observe(latency)


def track_db_error(operation: str, error_type: str):
    """Track database query errors."""
    DB_QUERY_ERRORS_TOTAL.labels(operation=operation, error_type=error_type).inc()


def set_active_connections(count: int):
    """Set the current number of active database connections."""
    DB_CONNECTIONS_ACTIVE.set(count)
