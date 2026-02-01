"""
Database helper utilities for common query patterns.
"""

from typing import TypeVar, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, status
from uuid import UUID

from src.platform.utils.exceptions import raise_not_found

T = TypeVar('T')


def get_or_404(
    db: Session,
    model: Type[T],
    resource_id: UUID,
    resource_name: Optional[str] = None
) -> T:
    """
    Get a resource by ID or raise 404 if not found.
    
    Usage:
        provider = get_or_404(db, Provider, provider_id, "Provider")
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        resource_id: Resource UUID
        resource_name: Human-readable resource name (defaults to model.__name__)
    
    Returns:
        Model instance
    
    Raises:
        HTTPException: 404 if resource not found
    """
    resource_name = resource_name or model.__name__
    resource = db.query(model).filter(model.id == resource_id).first()
    
    if not resource:
        raise raise_not_found(resource_name, str(resource_id))
    
    return resource


def get_or_none(
    db: Session,
    model: Type[T],
    resource_id: UUID
) -> Optional[T]:
    """
    Get a resource by ID or return None if not found.
    
    Usage:
        provider = get_or_none(db, Provider, provider_id)
        if not provider:
            return {"message": "Not found"}
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        resource_id: Resource UUID
    
    Returns:
        Model instance or None
    """
    return db.query(model).filter(model.id == resource_id).first()


def get_by_field_or_404(
    db: Session,
    model: Type[T],
    field_name: str,
    field_value: any,
    resource_name: Optional[str] = None
) -> T:
    """
    Get a resource by a specific field or raise 404 if not found.
    
    Usage:
        provider = get_by_field_or_404(db, Provider, "email", email, "Provider")
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        field_name: Field name to filter by
        field_value: Value to filter by
        resource_name: Human-readable resource name
    
    Returns:
        Model instance
    
    Raises:
        HTTPException: 404 if resource not found
    """
    resource_name = resource_name or model.__name__
    field = getattr(model, field_name)
    resource = db.query(model).filter(field == field_value).first()
    
    if not resource:
        raise raise_not_found(resource_name)
    
    return resource


def exists(
    db: Session,
    model: Type[T],
    resource_id: UUID
) -> bool:
    """
    Check if a resource exists by ID.
    
    Usage:
        if exists(db, Provider, provider_id):
            return {"message": "Exists"}
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        resource_id: Resource UUID
    
    Returns:
        True if exists, False otherwise
    """
    return db.query(model).filter(model.id == resource_id).first() is not None
