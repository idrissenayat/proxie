"""
Authentication utilities for Proxie.
Integrates with Clerk to verify JWT tokens and manage user sessions.
"""

import structlog
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_api import Clerk
from clerk_backend_api.security import verify_token as clerk_verify_token, VerifyTokenOptions
from sqlalchemy.orm import Session

from src.platform.config import settings
from src.platform.database import get_db
from src.platform.models.provider import Provider
from src.platform.models.consumer import Consumer
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.models.booking import Booking
from uuid import UUID

logger = structlog.get_logger(__name__)

# Initialize Clerk client
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

# Security scheme for bearer tokens
security = HTTPBearer(auto_error=False)

def verify_token(token: str) -> Dict[str, Any]:
    """Wrapper for clerk_verify_token with default options."""
    return clerk_verify_token(
        token,
        VerifyTokenOptions(
            secret_key=settings.CLERK_SECRET_KEY,
        )
    )

async def get_current_user(
    request: Request,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to verify the Clerk JWT token.
    Returns the decoded token (user info) if valid, or raises 401.
    """
    # LOAD TESTING/TESTING BYPASS
    if settings.ENVIRONMENT in ["testing", "development"]:
        # Allow bypass for load testing if X-Load-Test-Secret matches 
        bypass_secret = getattr(settings, "LOAD_TEST_SECRET", None)
        if bypass_secret and request.headers.get("X-Load-Test-Secret") == bypass_secret:
            logger.info("auth_bypass_success", type="load_test")
            return {
                "sub": request.headers.get("X-Test-User-Id", "mock_load_test_user"),
                "email": "loadtest@proxie.app",
                "public_metadata": {"role": request.headers.get("X-Test-User-Role", "consumer")}
            }

    if not auth:
        logger.warning("auth_missing", path=request.url.path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.credentials

    try:
        # Verify the token against Clerk's JWKS
        # Note: In production, verify_token handles local caching of keys
        decoded_token = verify_token(token)
        
        # Inject user info into log context
        structlog.contextvars.bind_contextvars(
            user_id=decoded_token.get("sub"),
            auth_type="clerk"
        )
        
        return decoded_token
        
    except Exception as e:
        logger.error("auth_verification_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    request: Request,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency that returns the decoded token if valid,
    or None if authentication is missing or invalid.
    Useful for endpoints that support both guest and authenticated users.
    """
    try:
        return await get_current_user(request, auth)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise e

def get_user_role_from_db(clerk_id: str, db: Session) -> Optional[str]:
    """
    Determine user role by checking database records.
    Returns 'provider' if Provider record exists, 'consumer' if Consumer record exists, None otherwise.
    """
    # Check if user is a provider
    provider = db.query(Provider).filter(Provider.clerk_id == clerk_id).first()
    if provider:
        return "provider"
    
    # Check if user is a consumer
    consumer = db.query(Consumer).filter(Consumer.clerk_id == clerk_id).first()
    if consumer:
        return "consumer"
    
    return None


def require_role(role: str):
    """
    Dependency factory to enforce role-based access control.
    
    Checks role in this order:
    1. Clerk public_metadata.role (if set)
    2. Database records (Provider/Consumer tables)
    
    Args:
        role: Required role ('provider', 'consumer', or 'admin')
    
    Returns:
        Dependency function that validates user has the required role
    """
    async def role_checker(
        user: Dict[str, Any] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        clerk_id = user.get("sub")
        if not clerk_id:
            logger.error("no_clerk_id_in_token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # 1. Check Clerk metadata first (highest priority)
        user_role = user.get("public_metadata", {}).get("role")
        
        # 2. Fallback: Check database records
        if not user_role:
            user_role = get_user_role_from_db(clerk_id, db)
            logger.debug("role_from_db", clerk_id=clerk_id, role=user_role)
        
        # 3. Admin role can access anything
        if user_role == "admin":
            return user
        
        # 4. Validate role matches requirement
        if not user_role or user_role != role:
            logger.warning(
                "role_mismatch",
                required=role,
                actual=user_role,
                clerk_id=clerk_id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Resource requires '{role}' role. Your role: '{user_role or 'none'}'",
            )
        
        return user
    
    return role_checker


def check_resource_ownership(
    resource_type: str,
    resource_id: UUID,
    clerk_id: str,
    db: Session,
    user: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Check if a user owns a resource.
    
    Args:
        resource_type: Type of resource ('provider', 'consumer', 'request', 'offer', 'booking')
        resource_id: ID of the resource
        clerk_id: Clerk ID of the user
        db: Database session
        user: Optional user dict (for admin check)
    
    Returns:
        True if user owns the resource, False otherwise
    """
    # Admin can access any resource
    if user and user.get("public_metadata", {}).get("role") == "admin":
        return True
    
    if resource_type == "provider":
        provider = db.query(Provider).filter(
            Provider.id == resource_id,
            Provider.clerk_id == clerk_id
        ).first()
        return provider is not None
        
    elif resource_type == "consumer":
        consumer = db.query(Consumer).filter(
            Consumer.id == resource_id,
            Consumer.clerk_id == clerk_id
        ).first()
        return consumer is not None
        
    elif resource_type == "request":
        request = db.query(ServiceRequest).filter(
            ServiceRequest.id == resource_id,
            ServiceRequest.consumer_id == clerk_id
        ).first()
        return request is not None
        
    elif resource_type == "offer":
        # Offers are owned by providers
        offer = db.query(Offer).filter(Offer.id == resource_id).first()
        if not offer:
            return False
        provider = db.query(Provider).filter(
            Provider.id == offer.provider_id,
            Provider.clerk_id == clerk_id
        ).first()
        return provider is not None
        
    elif resource_type == "booking":
        # Bookings can be owned by either consumer or provider
        booking = db.query(Booking).filter(Booking.id == resource_id).first()
        if not booking:
            return False
        
        # Check if user is the consumer
        if str(booking.consumer_id) == clerk_id:
            return True
        
        # Check if user is the provider
        provider = db.query(Provider).filter(
            Provider.id == booking.provider_id,
            Provider.clerk_id == clerk_id
        ).first()
        return provider is not None
        
    else:
        logger.error("unknown_resource_type", resource_type=resource_type)
        return False


def require_ownership(resource_type: str, resource_id: UUID, user: Dict[str, Any], db: Session):
    """
    Validate resource ownership and raise HTTPException if user doesn't own the resource.
    
    This is a helper function to be called within endpoint handlers.
    
    Args:
        resource_type: Type of resource ('provider', 'consumer', 'request', 'offer', 'booking')
        resource_id: ID of the resource
        user: Authenticated user dict
        db: Database session
    
    Raises:
        HTTPException: 403 if user doesn't own the resource
    """
    clerk_id = user.get("sub")
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    if not check_resource_ownership(resource_type, resource_id, clerk_id, db, user):
        logger.warning(
            "ownership_check_failed",
            resource_type=resource_type,
            resource_id=str(resource_id),
            clerk_id=clerk_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to access this {resource_type}"
        )
