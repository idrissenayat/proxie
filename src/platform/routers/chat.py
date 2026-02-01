"""
Chat router for Proxie.

Handles conversational AI interactions with multi-modal support.
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Header, Query
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.platform.schemas.chat import ChatRequest, ChatResponse, ChatTaskStatusResponse
from src.platform.services.chat import chat_service
from src.platform.config import settings
from src.platform.auth import get_current_user, get_optional_user
from src.platform.worker import celery_app
from typing import Dict, Any
from celery.result import AsyncResult

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


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send Chat Message",
    description="""
    Send a message to the Proxie AI Agent for conversational interaction.
    
    **Features:**
    - Natural language processing for request creation
    - Multi-modal support (text, images, files)
    - Context-aware conversations with session management
    - Tool calling for actions (create requests, get leads, etc.)
    
    **Modes:**
    - **Synchronous (default)**: Returns response immediately (2-5 seconds)
    - **Asynchronous**: Returns task_id immediately, poll `/chat/task/{task_id}` for result
    
    **Authentication:** Optional. Authenticated users get personalized responses.
    
    **Rate Limit:** 30 requests per minute (lower limit due to LLM processing).
    
    **Query Parameters:**
    - `async_mode`: Set to `true` to enable async processing
    """,
    responses={
        200: {
            "description": "Chat response received",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "session_123",
                        "message": "I can help you find a hairstylist in Brooklyn!",
                        "data": None,
                        "draft": None,
                        "awaiting_approval": False,
                        "task_id": None
                    }
                }
            }
        },
        200: {
            "description": "Task created (async mode)",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "session_123",
                        "message": "Processing your message...",
                        "data": {"task_id": "task_456", "status": "processing"},
                        "task_id": "task_456"
                    }
                }
            }
        },
        400: {"description": "Invalid request or LLM budget exceeded"},
        429: {"description": "Rate limit exceeded"}
    }
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    async_mode: bool = Query(False, description="Enable async processing via Celery")
):
    """
    Send a message to the Proxie AI Agent.
    
    Now secured via Clerk JWT. The consumer_id/provider_id in the request 
    body will be validated against the authenticated user.
    
    If async_mode=true or FEATURE_ASYNC_CHAT_ENABLED=true, the request will be
    processed asynchronously via Celery and return a task_id immediately.
    """
    # Security: Ensure user is only chatting as themselves
    clerk_id = None
    if user:
        clerk_id = user.get("sub")
        # chat_service.handle_chat will prioritize clerk_id to find/create the profile.
        # We don't need to overwrite consumer_id/provider_id in the request body
        # if it's already an authenticated session.

    # Check if async mode is enabled
    use_async = async_mode or settings.FEATURE_ASYNC_CHAT_ENABLED
    
    if use_async and not settings.CELERY_TASK_ALWAYS_EAGER:
        # Process asynchronously via Celery
        from src.platform.worker import process_chat_message_task
        
        # Convert media to dict for serialization
        media_dict = None
        if chat_request.media:
            media_dict = [
                m.model_dump() if hasattr(m, 'model_dump') else dict(m)
                for m in chat_request.media
            ]
        
        # Start async task
        task = process_chat_message_task.delay(
            message=chat_request.message or "",
            session_id=chat_request.session_id or "",
            role=chat_request.role,
            consumer_id=str(chat_request.consumer_id) if chat_request.consumer_id else None,
            provider_id=str(chat_request.provider_id) if chat_request.provider_id else None,
            enrollment_id=str(chat_request.enrollment_id) if chat_request.enrollment_id else None,
            media=media_dict,
            action=chat_request.action,
            clerk_id=clerk_id
        )
        
        # Return task ID immediately
        return ChatResponse(
            session_id=chat_request.session_id or "",
            message="Processing your message...",
            data={"task_id": task.id, "status": "processing"},
            draft=None,
            awaiting_approval=False,
            task_id=task.id
        )
    else:
        # Process synchronously (original behavior)
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
            awaiting_approval=awaiting_approval,
            task_id=None
        )


@router.get("/task/{task_id}", response_model=ChatTaskStatusResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def get_chat_task_status(
    request: Request,
    task_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get the status of an async chat processing task.
    
    Returns task status and result when completed.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    response_data = {
        "task_id": task_id,
        "status": task_result.state,
        "result": None,
        "error": None,
        "progress": None
    }
    
    if task_result.ready():
        if task_result.successful():
            response_data["result"] = task_result.result
            response_data["status"] = "SUCCESS"
        else:
            response_data["error"] = str(task_result.info)
            response_data["status"] = "FAILURE"
    elif task_result.state == "PROGRESS":
        response_data["progress"] = task_result.info.get("progress", 0)
    
    return ChatTaskStatusResponse(**response_data)
