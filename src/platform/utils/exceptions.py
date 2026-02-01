"""
Custom exceptions and error handling utilities for Proxie.

This module provides:
- Custom exception classes for domain-specific errors
- HTTPException factory functions with error codes
- Structured error responses for better debugging
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes for API responses."""
    # Authentication errors (1xxx)
    AUTH_REQUIRED = "AUTH_1001"
    AUTH_INVALID_TOKEN = "AUTH_1002"
    AUTH_EXPIRED_TOKEN = "AUTH_1003"
    AUTH_MISSING_USER_ID = "AUTH_1004"

    # Authorization errors (2xxx)
    FORBIDDEN_ROLE = "AUTHZ_2001"
    FORBIDDEN_OWNERSHIP = "AUTHZ_2002"
    FORBIDDEN_ACTION = "AUTHZ_2003"

    # Resource errors (3xxx)
    NOT_FOUND = "RES_3001"
    NOT_FOUND_PROVIDER = "RES_3002"
    NOT_FOUND_CONSUMER = "RES_3003"
    NOT_FOUND_REQUEST = "RES_3004"
    NOT_FOUND_OFFER = "RES_3005"
    NOT_FOUND_BOOKING = "RES_3006"
    NOT_FOUND_SESSION = "RES_3007"

    # Validation errors (4xxx)
    VALIDATION_FAILED = "VAL_4001"
    VALIDATION_FIELD = "VAL_4002"
    VALIDATION_CONSTRAINT = "VAL_4003"

    # Conflict errors (5xxx)
    CONFLICT_DUPLICATE = "CONF_5001"
    CONFLICT_STATE = "CONF_5002"

    # Rate limiting errors (6xxx)
    RATE_LIMIT_EXCEEDED = "RATE_6001"
    BUDGET_EXCEEDED = "RATE_6002"

    # External service errors (7xxx)
    LLM_ERROR = "EXT_7001"
    LLM_TIMEOUT = "EXT_7002"
    REDIS_ERROR = "EXT_7003"
    DATABASE_ERROR = "EXT_7004"

    # Internal errors (9xxx)
    INTERNAL_ERROR = "INT_9001"
    CONFIGURATION_ERROR = "INT_9002"


class ProxieException(Exception):
    """Base exception for Proxie-specific errors."""

    def __init__(
        self,
        message: str,
        code: Optional[ErrorCode] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code or ErrorCode.INTERNAL_ERROR
        self.context = context or {}
        super().__init__(message)


class ResourceNotFound(ProxieException):
    """Raised when a requested resource is not found."""

    RESOURCE_CODES = {
        "provider": ErrorCode.NOT_FOUND_PROVIDER,
        "consumer": ErrorCode.NOT_FOUND_CONSUMER,
        "request": ErrorCode.NOT_FOUND_REQUEST,
        "offer": ErrorCode.NOT_FOUND_OFFER,
        "booking": ErrorCode.NOT_FOUND_BOOKING,
        "session": ErrorCode.NOT_FOUND_SESSION,
    }

    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (id: {resource_id})"

        code = self.RESOURCE_CODES.get(resource_type.lower(), ErrorCode.NOT_FOUND)
        context = {"resource_type": resource_type}
        if resource_id:
            context["resource_id"] = resource_id

        super().__init__(message, code, context)


class UnauthorizedAccess(ProxieException):
    """Raised when user is not authorized to access a resource."""

    def __init__(self, resource_type: str, action: str = "access"):
        self.resource_type = resource_type
        self.action = action
        super().__init__(
            message=f"Not authorized to {action} this {resource_type}",
            code=ErrorCode.FORBIDDEN_OWNERSHIP,
            context={"resource_type": resource_type, "action": action}
        )


class ValidationError(ProxieException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, errors: Optional[List[Dict]] = None):
        self.field = field
        self.errors = errors or []
        context = {}
        if field:
            context["field"] = field
        if errors:
            context["errors"] = errors
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_FIELD if field else ErrorCode.VALIDATION_FAILED,
            context=context
        )


class RateLimitExceeded(ProxieException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        limit_type: str = "request"
    ):
        self.retry_after = retry_after
        self.limit_type = limit_type
        context = {"limit_type": limit_type}
        if retry_after:
            context["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            context=context
        )


class BudgetExceeded(ProxieException):
    """Raised when LLM budget limit is exceeded."""

    def __init__(
        self,
        message: str = "LLM usage limit exceeded",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        current_usage: Optional[float] = None,
        limit: Optional[float] = None
    ):
        context = {}
        if user_id:
            context["user_id"] = user_id
        if session_id:
            context["session_id"] = session_id
        if current_usage is not None:
            context["current_usage"] = current_usage
        if limit is not None:
            context["limit"] = limit
        super().__init__(
            message=message,
            code=ErrorCode.BUDGET_EXCEEDED,
            context=context
        )


class ExternalServiceError(ProxieException):
    """Raised when an external service fails."""

    def __init__(
        self,
        service: str,
        message: str,
        original_error: Optional[Exception] = None
    ):
        self.service = service
        self.original_error = original_error

        code_map = {
            "llm": ErrorCode.LLM_ERROR,
            "redis": ErrorCode.REDIS_ERROR,
            "database": ErrorCode.DATABASE_ERROR,
        }

        context = {"service": service}
        if original_error:
            context["original_error"] = str(original_error)

        super().__init__(
            message=message,
            code=code_map.get(service.lower(), ErrorCode.INTERNAL_ERROR),
            context=context
        )


# --- HTTPException Factory Functions ---

def create_error_detail(
    message: str,
    code: ErrorCode,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a structured error detail dictionary."""
    detail = {
        "message": message,
        "error_code": code.value,
    }
    if context:
        detail["context"] = context
    return detail


def raise_not_found(
    resource_type: str,
    resource_id: Optional[str] = None,
    message: Optional[str] = None
) -> HTTPException:
    """
    Raise a 404 HTTPException for a not found resource.

    Usage:
        raise raise_not_found("Provider", provider_id)
        raise raise_not_found("Provider", provider_id, "Provider profile not found")
    """
    exc = ResourceNotFound(resource_type, resource_id)
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=create_error_detail(
            message or exc.message,
            exc.code,
            exc.context
        )
    )


def raise_forbidden(
    message: str = "Not authorized",
    code: ErrorCode = ErrorCode.FORBIDDEN_ACTION,
    context: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Raise a 403 HTTPException for unauthorized access.

    Usage:
        raise raise_forbidden("Not authorized to edit this profile")
        raise raise_forbidden("Role mismatch", code=ErrorCode.FORBIDDEN_ROLE, context={"required": "admin"})
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=create_error_detail(message, code, context)
    )


def raise_bad_request(
    message: str,
    field: Optional[str] = None,
    code: ErrorCode = ErrorCode.VALIDATION_FAILED,
    context: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Raise a 400 HTTPException for bad requests.

    Usage:
        raise raise_bad_request("Invalid input data")
        raise raise_bad_request("Email is invalid", field="email")
    """
    ctx = context or {}
    if field:
        ctx["field"] = field
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=create_error_detail(message, code, ctx if ctx else None)
    )


def raise_conflict(
    message: str,
    code: ErrorCode = ErrorCode.CONFLICT_DUPLICATE,
    context: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Raise a 409 HTTPException for conflicts.

    Usage:
        raise raise_conflict("Resource already exists")
        raise raise_conflict("Provider email already registered", context={"email": email})
    """
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=create_error_detail(message, code, context)
    )


def raise_rate_limit(
    message: str = "Rate limit exceeded. Please try again later.",
    retry_after: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Raise a 429 HTTPException for rate limiting.

    Usage:
        raise raise_rate_limit("Too many requests", retry_after=60)
    """
    headers = {}
    if retry_after:
        headers["Retry-After"] = str(retry_after)

    ctx = context or {}
    if retry_after:
        ctx["retry_after_seconds"] = retry_after

    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=create_error_detail(message, ErrorCode.RATE_LIMIT_EXCEEDED, ctx if ctx else None),
        headers=headers if headers else None
    )


def raise_service_unavailable(
    service: str,
    message: Optional[str] = None,
    retry_after: Optional[int] = None
) -> HTTPException:
    """
    Raise a 503 HTTPException for service unavailability.

    Usage:
        raise raise_service_unavailable("LLM", "AI service temporarily unavailable")
    """
    headers = {}
    if retry_after:
        headers["Retry-After"] = str(retry_after)

    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=create_error_detail(
            message or f"{service} service temporarily unavailable",
            ErrorCode.LLM_ERROR if service.lower() == "llm" else ErrorCode.INTERNAL_ERROR,
            {"service": service}
        ),
        headers=headers if headers else None
    )
