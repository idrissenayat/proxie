"""
Utility modules for Proxie platform.
"""

from src.platform.utils.exceptions import (
    ProxieException,
    ResourceNotFound,
    UnauthorizedAccess,
    ValidationError,
    raise_not_found,
    raise_forbidden,
    raise_bad_request,
    raise_conflict
)

from src.platform.utils.db_helpers import (
    get_or_404,
    get_or_none,
    get_by_field_or_404,
    exists
)

from src.platform.utils.responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    success_response,
    error_response,
    paginated_response
)

__all__ = [
    # Exceptions
    "ProxieException",
    "ResourceNotFound",
    "UnauthorizedAccess",
    "ValidationError",
    "raise_not_found",
    "raise_forbidden",
    "raise_bad_request",
    "raise_conflict",
    # DB Helpers
    "get_or_404",
    "get_or_none",
    "get_by_field_or_404",
    "exists",
    # Responses
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "success_response",
    "error_response",
    "paginated_response",
]
