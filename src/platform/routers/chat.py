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
    _: bool = Depends(verify_chat_api_key)
):
    """
    Send a message to the Proxie AI Agent.
    
    Supports:
    - Text messages
    - Media attachments (images, videos)
    - Workflow actions (approve/edit/cancel requests)
    
    If CHAT_API_KEY is set in environment, requires X-API-Key header.
    Rate limited to prevent abuse.
    """
    session_id, response_msg, data, draft, awaiting_approval = await chat_service.handle_chat(
        message=chat_request.message,
        session_id=chat_request.session_id,
        role=chat_request.role,
        consumer_id=chat_request.consumer_id,
        provider_id=chat_request.provider_id,
        enrollment_id=chat_request.enrollment_id,
        media=chat_request.media,
        action=chat_request.action
    )
    
    return ChatResponse(
        session_id=session_id,
        message=response_msg,
        data=data,
        draft=draft,
        awaiting_approval=awaiting_approval
    )
