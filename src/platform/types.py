"""
Type definitions for Proxie platform.

This module provides TypedDict definitions for commonly used dictionary structures
to improve type safety and IDE support throughout the codebase.
"""

from typing import TypedDict, Optional, List, Literal, NotRequired
from uuid import UUID


# --- Authentication Types ---

class ClerkPublicMetadata(TypedDict, total=False):
    """Clerk public metadata structure."""
    role: Literal["consumer", "provider", "admin"]


class AuthenticatedUser(TypedDict):
    """Decoded JWT token / authenticated user information."""
    sub: str  # Clerk user ID
    email: NotRequired[str]
    public_metadata: NotRequired[ClerkPublicMetadata]
    # Additional Clerk token fields
    iss: NotRequired[str]
    iat: NotRequired[int]
    exp: NotRequired[int]


class TestUser(TypedDict):
    """Test/load test user for auth bypass."""
    sub: str
    email: str
    public_metadata: ClerkPublicMetadata


# --- Location Types ---

class LocationInfo(TypedDict, total=False):
    """Location information structure."""
    city: str
    neighborhood: NotRequired[str]
    state: NotRequired[str]
    country: NotRequired[str]
    latitude: NotRequired[float]
    longitude: NotRequired[float]


# --- Budget Types ---

class BudgetRange(TypedDict, total=False):
    """Budget range structure."""
    min: float
    max: float
    currency: NotRequired[str]


# --- Timing Types ---

class TimingInfo(TypedDict, total=False):
    """Timing preference structure."""
    urgency: Literal["asap", "flexible", "specific_date"]
    preferred_date: NotRequired[str]
    preferred_time: NotRequired[str]
    time_window: NotRequired[str]


# --- Service Request Types ---

class ServiceRequirements(TypedDict, total=False):
    """Service requirements structure."""
    specializations: NotRequired[List[str]]
    experience_level: NotRequired[str]
    certifications: NotRequired[List[str]]
    custom_requirements: NotRequired[str]


class ServiceRequestDetails(TypedDict, total=False):
    """Additional service request details."""
    hair_type: NotRequired[str]
    hair_length: NotRequired[str]
    desired_style: NotRequired[str]
    special_requests: NotRequired[str]


# --- Chat/Message Types ---

class ChatMessage(TypedDict, total=False):
    """Chat message structure for LLM interactions."""
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str]
    name: NotRequired[str]
    tool_calls: NotRequired[List["ToolCall"]]
    tool_call_id: NotRequired[str]


class ToolCall(TypedDict):
    """LLM tool call structure."""
    id: str
    type: Literal["function"]
    function: "FunctionCall"


class FunctionCall(TypedDict):
    """Function call within a tool call."""
    name: str
    arguments: str  # JSON string


# --- LLM Response Types ---

class LLMUsage(TypedDict):
    """LLM token usage structure."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMChoice(TypedDict):
    """LLM response choice structure."""
    message: ChatMessage
    finish_reason: str
    index: NotRequired[int]


class LLMResponse(TypedDict):
    """LLM completion response structure."""
    choices: List[LLMChoice]
    usage: LLMUsage
    model: NotRequired[str]
    id: NotRequired[str]


# --- Session Types ---

class SessionContext(TypedDict, total=False):
    """Session context information."""
    user_id: str
    role: Literal["consumer", "provider"]
    consumer_id: NotRequired[str]
    provider_id: NotRequired[str]
    enrollment_id: NotRequired[str]
    current_intent: NotRequired[str]
    gathered_info: NotRequired[dict]


class SessionData(TypedDict, total=False):
    """Full session data structure."""
    session_id: str
    context: SessionContext
    messages: List[ChatMessage]
    created_at: str
    updated_at: str
    expires_at: NotRequired[str]


# --- Provider Types ---

class ProviderMatch(TypedDict):
    """Provider match result from matching service."""
    id: UUID
    score: float
    distance: NotRequired[float]
    name: NotRequired[str]
    specializations: NotRequired[List[str]]


class ProviderSearchFilters(TypedDict, total=False):
    """Filters for provider search."""
    category: NotRequired[str]
    city: NotRequired[str]
    specializations: NotRequired[List[str]]
    min_rating: NotRequired[float]
    max_distance: NotRequired[float]


# --- Error Types ---

class ErrorDetail(TypedDict):
    """Structured error detail."""
    code: str
    message: str
    field: NotRequired[str]
    context: NotRequired[dict]


class ErrorResponse(TypedDict):
    """API error response structure."""
    detail: str
    error_code: NotRequired[str]
    errors: NotRequired[List[ErrorDetail]]


# --- Webhook Types ---

class WebhookPayload(TypedDict, total=False):
    """Generic webhook payload structure."""
    event: str
    timestamp: str
    data: dict


# --- Metrics Types ---

class UsageMetrics(TypedDict):
    """LLM usage metrics for cost tracking."""
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_cents: float
    user_id: NotRequired[str]
    session_id: NotRequired[str]
