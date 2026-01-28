"""
Authentication utilities for Proxie.
Integrates with Clerk to verify JWT tokens and manage user sessions.
"""

import structlog
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import verify_token

from src.platform.config import settings

logger = structlog.get_logger(__name__)

# Initialize Clerk client
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

# Security scheme for bearer tokens
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to verify the Clerk JWT token.
    Returns the decoded token (user info) if valid, or raises 401.
    """
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

def require_role(role: str):
    """
    Dependency factory to enforce role-based access.
    Note: Requires Clerk public metadata or roles to be synchronized.
    """
    async def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        # Clerk stores metadata in 'public_metadata' or 'private_metadata'
        # For the pilot, we might use a sync script or manual metadata
        user_role = user.get("public_metadata", {}).get("role")
        
        if not user_role or user_role != role:
            logger.warning("role_mismatch", required=role, actual=user_role)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Resource requires '{role}' role",
            )
        return user
    
    return role_checker
