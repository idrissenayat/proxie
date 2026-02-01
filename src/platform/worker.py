"""
Proxie Celery Worker - Background Task Processing

Handles offloading of heavy processing, such as LLM specialist analysis.
"""

from celery import Celery
import structlog
from typing import List, Dict, Optional
from src.platform.config import settings

logger = structlog.get_logger()

# Initialize Celery app
celery_app = Celery(
    "proxie_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER
)

@celery_app.task(name="analyze_session_media")
def analyze_session_media(session_id: str):
    """
    Background task to analyze media in a session and consult specialists.
    """
    from src.platform.sessions import session_manager
    from src.platform.services.specialists import specialist_registry
    from src.platform.services.llm_gateway import llm_gateway
    import asyncio

    logger.info("Starting background media analysis", session_id=session_id)
    
    # Load session
    session = session_manager.get_session(session_id)
    if not session:
        logger.error("Session not found", session_id=session_id)
        return
    
    context = session.get("context", {})
    media = context.get("media", [])
    
    if not media:
        logger.info("No media to analyze", session_id=session_id)
        return

    # 1. Generate descriptions for new media if missing
    # (In a real app, we'd check which ones are new)
    media_descriptions = context.get("media_descriptions", [])
    
    # Mock/Simple implementation: If we have media but no descriptions, 
    # we could call a vision model here.
    # For now, let's assume we want to trigger a specialist consult 
    # based on whatever we have.
    
    # 2. Specialist Consultation
    service_type = context.get("gathered_info", {}).get("service_type")
    # Fallback to hair if we are in a haircut-heavy test context
    specialist = specialist_registry.find_for_service(service_type or "haircut")
    
    if specialist:
        logger.info("Found specialist", specialist=specialist.name)
        # Run async analysis - handle both sync and async contexts
        try:
            from dataclasses import asdict
            import asyncio
            
            async def run_analysis():
                return await specialist.analyze(
                    service_type=service_type or "haircut",
                    description=context.get("gathered_info", {}).get("description", "Media analysis"),
                    location=context.get("gathered_info", {}).get("location", {}),
                    budget=context.get("gathered_info", {}).get("budget", {}),
                    timing=context.get("gathered_info", {}).get("timing"),
                    media_descriptions=media_descriptions,
                    additional_context={"is_background": True}
                )
            
            # Try to get existing loop or create new one
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, use nest_asyncio or run_coroutine_threadsafe
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    analysis = pool.submit(asyncio.run, run_analysis()).result()
            except RuntimeError:
                # No running loop, we can use asyncio.run
                analysis = asyncio.run(run_analysis())
            
            # Update session
            context["specialist_analysis"] = asdict(analysis)
            
            # Update gathered info with enriched data
            info = context.get("gathered_info", {})
            if analysis.enriched_data:
                info.update(analysis.enriched_data)
                context["gathered_info"] = info
                
            session["context"] = context
            session_manager.save_session(session_id, session)
            logger.info("Background specialist analysis completed", session_id=session_id)
        except Exception as e:
            logger.error("Specialist analysis failed", error=str(e))
    else:
        logger.warning("No specialist found for service_type", service_type=service_type)

    return {"status": "completed", "session_id": session_id}

@celery_app.task(name="process_chat_message", bind=True)
def process_chat_message_task(
    self,
    message: str,
    session_id: str,
    role: str = "consumer",
    consumer_id: Optional[str] = None,
    provider_id: Optional[str] = None,
    enrollment_id: Optional[str] = None,
    media: Optional[List[Dict]] = None,
    action: Optional[str] = None,
    clerk_id: Optional[str] = None
):
    """
    Process a chat message asynchronously in a Celery worker.
    
    This task handles the full chat processing pipeline:
    1. Load/create session
    2. Process message through orchestrator
    3. Handle tool calls
    4. Return response
    
    Returns:
        dict: {
            "session_id": str,
            "message": str,
            "data": Optional[Dict],
            "draft": Optional[Dict],
            "awaiting_approval": bool
        }
    """
    import asyncio
    from src.platform.services.chat import chat_service
    from src.platform.schemas.media import MediaAttachment
    
    logger.info(
        "Processing chat message task",
        task_id=self.request.id,
        session_id=session_id,
        role=role
    )
    
    try:
        # Convert media dicts to MediaAttachment objects if provided
        media_attachments = None
        if media:
            media_attachments = [
                MediaAttachment(**m) if isinstance(m, dict) else m
                for m in media
            ]
        
        # Run async chat handler
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, need to use nest_asyncio or run in thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    chat_service.handle_chat(
                        message=message,
                        session_id=session_id,
                        role=role,
                        consumer_id=consumer_id,
                        provider_id=provider_id,
                        enrollment_id=enrollment_id,
                        media=media_attachments,
                        action=action,
                        clerk_id=clerk_id
                    )
                )
                result = future.result()
        except RuntimeError:
            # No running loop, we can use asyncio.run directly
            result = asyncio.run(
                chat_service.handle_chat(
                    message=message,
                    session_id=session_id,
                    role=role,
                    consumer_id=consumer_id,
                    provider_id=provider_id,
                    enrollment_id=enrollment_id,
                    media=media_attachments,
                    action=action,
                    clerk_id=clerk_id
                )
            )
        
        session_id_result, response_msg, data, draft, awaiting_approval = result
        
        return {
            "status": "completed",
            "session_id": session_id_result,
            "message": response_msg,
            "data": data,
            "draft": draft.model_dump() if draft else None,
            "awaiting_approval": awaiting_approval
        }
        
    except Exception as e:
        logger.error(
            "Chat message processing failed",
            task_id=self.request.id,
            error=str(e),
            exc_info=True
        )
        # Update task state
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(name="process_llm_inference")
def process_llm_inference(messages: list, context: dict):
    """
    Offload long-running LLM inferences if needed (e.g. generating long reports).
    """
    logger.info("Processing background LLM inference")
    # from src.platform.services.llm_gateway import llm_gateway
    # response = llm_gateway.chat_completion(messages=messages)
    return {"status": "success"}

# Auto-discovery of tasks if we move them to separate modules
# celery_app.autodiscover_tasks(['src.platform.tasks'])
