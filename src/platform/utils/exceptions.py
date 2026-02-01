"""
Custom exceptions and error handling utilities for Proxie.
"""

from fastapi import HTTPException, status
from typing import Optional


class ProxieException(Exception):
    """Base exception for Proxie-specific errors."""
    pass


class ResourceNotFound(ProxieException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (id: {resource_id})"
        super().__init__(message)


class UnauthorizedAccess(ProxieException):
    """Raised when user is not authorized to access a resource."""
    def __init__(self, resource_type: str, action: str = "access"):
        self.resource_type = resource_type
        self.action = action
        super().__init__(f"Not authorized to {action} this {resource_type}")


class ValidationError(ProxieException):
    """Raised when validation fails."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


def raise_not_found(resource_type: str, resource_id: Optional[str] = None) -> HTTPException:
    """
    Raise a 404 HTTPException for a not found resource.
    
    Usage:
        raise raise_not_found("Provider", provider_id)
    """
    detail = f"{resource_type} not found"
    if resource_id:
        detail += f" (id: {resource_id})"
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def raise_forbidden(message: str = "Not authorized") -> HTTPException:
    """
    Raise a 403 HTTPException for unauthorized access.
    
    Usage:
        raise raise_forbidden("Not authorized to edit this profile")
    """
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def raise_bad_request(message: str) -> HTTPException:
    """
    Raise a 400 HTTPException for bad requests.
    
    Usage:
        raise raise_bad_request("Invalid input data")
    """
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def raise_conflict(message: str) -> HTTPException:
    """
    Raise a 409 HTTPException for conflicts.
    
    Usage:
        raise raise_conflict("Resource already exists")
    """
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
