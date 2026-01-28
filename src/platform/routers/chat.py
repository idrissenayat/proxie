"""
Chat router for Proxie.

Handles conversational AI interactions with multi-modal support.
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Header
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.platform.schemas.chat import ChatRequest, ChatResponse
from src.platform.services.chat import chat_service
from src.platform.config import settings
from src.platform.auth import get_current_user, get_optional_user
from typing import Dict, Any

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

limiter = Limiter(key_func=get_remote_address)


async def verify_chat_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify API key for chat endpoint if CHAT_API_KEY is configured.
    If CHAT_API_KEY is empty, no authentication is required.
    """
    if settings.CHAT_API_KEY:
        if not x_api_key:
            raise HTTPException(
                status_code=401,
                detail="X-API-Key header required",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        if x_api_key != settings.CHAT_API_KEY:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key",
            )
    return True


@router.post("/", response_model=ChatResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Send a message to the Proxie AI Agent.
    
    Now secured via Clerk JWT. The consumer_id/provider_id in the request 
    body will be validated against the authenticated user.
    """
    # Security: Ensure user is only chatting as themselves
    clerk_id = None
    if user:
        clerk_id = user.get("sub")
        if chat_request.consumer_id and str(chat_request.consumer_id) != clerk_id:
             chat_request.consumer_id = clerk_id
        
        if chat_request.provider_id and str(chat_request.provider_id) != clerk_id:
             chat_request.provider_id = clerk_id

    session_id, response_msg, data, draft, awaiting_approval = await chat_service.handle_chat(
        message=chat_request.message,
        session_id=chat_request.session_id,
        role=chat_request.role,
        consumer_id=chat_request.consumer_id,
        provider_id=chat_request.provider_id,
        enrollment_id=chat_request.enrollment_id,
        media=chat_request.media,
        action=chat_request.action,
        clerk_id=clerk_id
    )
    
    return ChatResponse(
        session_id=session_id,
        message=response_msg,
        data=data,
        draft=draft,
        awaiting_approval=awaiting_approval
    )
