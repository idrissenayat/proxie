"""
Response formatting utilities for consistent API responses.
"""

from typing import Optional, Dict, Any, List
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Standard success response format."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Standard paginated response format."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int


def success_response(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Create a standardized success response.
    
    Usage:
        return success_response(data={"id": "123"}, message="Created successfully")
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
    
    Returns:
        JSONResponse with standardized format
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )


def error_response(
    error: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Usage:
        return error_response("Validation failed", details={"field": "email"})
    
    Args:
        error: Error message
        details: Additional error details
        status_code: HTTP status code
    
    Returns:
        JSONResponse with standardized format
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error,
            "details": details
        }
    )


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int
) -> Dict[str, Any]:
    """
    Create a standardized paginated response.
    
    Usage:
        return paginated_response(items, total=100, page=1, per_page=20)
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (1-indexed)
        per_page: Items per page
    
    Returns:
        Dictionary with pagination metadata
    """
    pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }
