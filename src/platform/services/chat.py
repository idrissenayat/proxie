"""
Proxie Chat Service - Gemini Integration with Multi-Modal Support

Handles conversational AI interactions using Google's Gemini API,
including image/video understanding and specialist consultation.
"""

import json
import logging
import base64
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from src.platform.config import settings
from src.mcp import handlers
from src.platform.schemas.media import MediaAttachment, StoredMedia
from src.platform.schemas.chat import DraftRequest
from src.platform.services.media import media_service
from src.platform.services.specialists import specialist_registry
from src.platform.services.suggestions import suggestion_service

logger = logging.getLogger(__name__)

CONSUMER_SYSTEM_PROMPT = """You are the Proxie Consumer Agent, a helpful concierge for users looking for services.
Your goal: Help users gather all necessary info (location, budget, timing) and share media to create a perfect service request.

Capabilities:
- Analyze photos to identify hair types or service needs.
- Prepare draft requests and ask for approval.
- Post requests to the live marketplace via 'create_service_request'.
- List and help select provider offers via 'get_offers' and 'accept_offer'.
"""

PROVIDER_SYSTEM_PROMPT = """You are the Proxie Provider Agent, an AI companion helping skilled professionals manage their business and leads.
Your context: You have access to {provider_name}'s profile, services, and availability.

Your goal:
- Help providers browse and understand their leads (matching requests).
- Explain technical details from 'specialist_analysis' found in leads.
- Use 'suggest_offer' to recommend pricing and timing based on complexity.
- Assist in drafting and submitting professional offers.
- Help tracking lead status (new vs. viewed).

Tools you can use:
- 'get_my_leads': Lists all requests that match the provider's skills.
- 'get_lead_details': Gets full info including consumer media and specialist notes.
- 'suggest_offer': Gets AI advice on pricing and availability.
- 'draft_offer': Prepares a draft for the provider's review.
- 'submit_offer': Sends the final offer to the consumer.

Rules:
- Never submit an offer without the provider's approval.
- Be professional, efficient, and proactive in identifying high-value leads.
"""

ENROLLMENT_SYSTEM_PROMPT = """You are the Enrollment Agent for Proxie, helping new service providers join the platform.

Your goal: Guide providers through enrollment in a friendly, conversational way. Collect all required information while making the process feel easy and quick.

Process to follow:
1. Welcome and explain the enrollment journey.
2. Collect profile info (name, business name, phone, email).
3. Select services from the catalog using 'get_service_catalog'. help map their work to specific service types.
4. Set pricing and durating for each service.
5. Set location and service radius.
6. Collect weekly availability.
7. Portfolio: encourage 3-10 photos. Use vision to describe and categorize their work.
8. Bio: help them draft a professional bio based on their story.
9. Review: Show a summary of their enrollment before submission.

Rules:
- Be encouraging and positive.
- One question at a time.
- Confirm info before saving using tools.
- If they seem stuck, suggest typical pricing or durations from catalog metadata.
"""

# Keep general prompt as fallback
SYSTEM_PROMPT = CONSUMER_SYSTEM_PROMPT

# Tool definitions
ENROLLMENT_TOOL_DECLARATIONS = [
    FunctionDeclaration(
        name="get_service_catalog",
        description="Get the list of service categories and services available on the platform.",
        parameters={"type": "object", "properties": {}}
    ),
    FunctionDeclaration(
        name="update_enrollment",
        description="Update provider enrollment data (profile, location, services, etc.) as it's collected.",
        parameters={
            "type": "object",
            "properties": {
                "full_name": {"type": "string"},
                "business_name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "location": {"type": "object", "description": "City, address, radius, etc."},
                "services": {"type": "array", "items": {"type": "object"}, "description": "List of services with price_min, price_max, etc."},
                "availability": {"type": "object", "description": "Weekly schedule"},
                "bio": {"type": "string"}
            }
        }
    ),
    FunctionDeclaration(
        name="get_enrollment_summary",
        description="Get the current enrollment summary for review.",
        parameters={"type": "object", "properties": {}}
    ),
    FunctionDeclaration(
        name="request_portfolio",
        description="Trigger the portfolio upload interface for the provider.",
        parameters={"type": "object", "properties": {}}
    ),
    FunctionDeclaration(
        name="submit_enrollment",
        description="Finalize and submit the enrollment for verification. Only call after user review.",
        parameters={"type": "object", "properties": {}}
    )
]

TOOL_DECLARATIONS = [
    FunctionDeclaration(
        name="create_service_request",
        description="Create a service request AFTER user has approved the draft. This posts the request to find providers.",
        parameters={
            "type": "object",
            "properties": {
                "service_type": {"type": "string", "description": "Type of service needed"},
                "description": {"type": "string", "description": "Detailed description of the request"},
                "city": {"type": "string", "description": "City where service is needed"},
                "budget_min": {"type": "number", "description": "Minimum budget in dollars"},
                "budget_max": {"type": "number", "description": "Maximum budget in dollars"},
                "timing": {"type": "string", "description": "When the service is needed"},
                "hair_type": {"type": "string", "description": "Hair type if hair service (e.g., '3B curly')"},
                "style_preferences": {"type": "string", "description": "Style preferences if relevant"}
            },
            "required": ["service_type", "city", "budget_min", "budget_max"]
        }
    ),
    FunctionDeclaration(
        name="get_offers",
        description="Get offers from providers for a service request",
        parameters={
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "description": "The service request ID"}
            },
            "required": ["request_id"]
        }
    ),
    FunctionDeclaration(
        name="accept_offer",
        description="Accept an offer and create a confirmed booking. Only call after user explicitly confirms.",
        parameters={
            "type": "object",
            "properties": {
                "offer_id": {"type": "string", "description": "The offer ID to accept"},
                "slot_date": {"type": "string", "description": "Selected date in YYYY-MM-DD format"},
                "slot_start_time": {"type": "string", "description": "Selected time in HH:MM format"}
            },
            "required": ["offer_id", "slot_date", "slot_start_time"]
        }
    ),
    FunctionDeclaration(
        name="get_my_leads",
        description="List all new and matching service requests for a provider.",
        parameters={
            "type": "object",
            "properties": {
                "provider_id": {"type": "string", "description": "The provider ID"}
            },
            "required": ["provider_id"]
        }
    ),
    FunctionDeclaration(
        name="get_lead_details",
        description="Get full details for a specific lead, including consumer photos, descriptions, and specialist analysis.",
        parameters={
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "description": "The lead/request ID"}
            },
            "required": ["request_id"]
        }
    ),
    FunctionDeclaration(
        name="suggest_offer",
        description="Get AI suggestions for pricing, timing, and response message for a specific lead.",
        parameters={
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "description": "The lead ID"},
                "provider_id": {"type": "string", "description": "The provider ID"}
            },
            "required": ["request_id", "provider_id"]
        }
    ),
    FunctionDeclaration(
        name="draft_offer",
        description="Draft an offer for provider review. Use after 'suggest_offer' or when provider gives price/time.",
        parameters={
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "description": "The lead ID"},
                "price": {"type": "number", "description": "Offered price"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "description": "HH:MM"},
                "message": {"type": "string", "description": "Message to consumer"}
            },
            "required": ["request_id", "price"]
        }
    ),
    FunctionDeclaration(
        name="submit_offer",
        description="Final submit of an offer AFTER provider has approved the draft.",
        parameters={
            "type": "object",
            "properties": {
                "draft_id": {"type": "string", "description": "The ID of the approved draft"}
            },
            "required": ["draft_id"]
        }
    )
]

# In-memory session storage
sessions: Dict[str, Dict[str, Any]] = {}


class ChatService:
    def __init__(self):
        self.is_mock = self._is_mock_mode()
        if not self.is_mock:
            genai.configure(api_key=settings.GOOGLE_API_KEY)

    def _is_mock_mode(self) -> bool:
        return not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY in ["", "your-gemini-api-key", "your-key-here"]

    def _get_model(self, role: str, provider_id: Optional[UUID] = None) -> Any:
        """Get a specialized model instance based on role."""
        if self.is_mock:
            return None
            
        prompt = CONSUMER_SYSTEM_PROMPT
        tools = TOOL_DECLARATIONS
        
        if role == "provider" and provider_id:
            provider_info = handlers.get_provider(provider_id)
            if "error" not in provider_info:
                prompt = PROVIDER_SYSTEM_PROMPT.format(
                    provider_name=provider_info.get("name", "Provider"),
                    provider_services=", ".join(provider_info.get("specializations", [])),
                    provider_pricing="standard rates",
                    provider_availability=str(provider_info.get("availability", "flexible"))
                )
        elif role == "enrollment":
            prompt = ENROLLMENT_SYSTEM_PROMPT
            tools = ENROLLMENT_TOOL_DECLARATIONS
        
        return genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=prompt,
            tools=[Tool(function_declarations=tools)]
        )

    def _get_or_create_session(self, session_id: Optional[str], role: str, provider_id: Optional[UUID]) -> Tuple[str, Dict]:
        """Get existing session or create a new one."""
        if not session_id:
            session_id = str(uuid4())
        
        if session_id not in sessions:
            if not self.is_mock:
                model = self._get_model(role, provider_id)
                chat = model.start_chat(history=[])
            else:
                chat = None
            
            sessions[session_id] = {
                "chat": chat,
                "context": {
                    "role": role,
                    "provider_id": str(provider_id) if provider_id else None,
                    "current_request_id": None,
                    "current_offers": [],
                    "gathered_info": {},  # Info gathered during conversation
                    "media": [],  # Attached media
                    "media_descriptions": [],  # AI descriptions of media
                    "draft": None,  # Current draft request
                    "awaiting_approval": False,
                },
                "specialist_feedback": None,
            }
        
        return session_id, sessions[session_id]

    async def handle_chat(
        self, 
        message: Optional[str],
        session_id: Optional[str] = None, 
        role: str = "consumer",
        consumer_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        enrollment_id: Optional[UUID] = None,
        media: Optional[List[MediaAttachment]] = None,
        action: Optional[str] = None
    ) -> Tuple[str, str, Optional[Dict[str, Any]], Optional[DraftRequest], bool]:
        """
        Handle a chat message and return response.
        
        Returns: (session_id, response_text, data, draft, awaiting_approval)
        """
        session_id, session = self._get_or_create_session(session_id, role, provider_id)
        session["context"]["role"] = role
        if consumer_id:
            session["context"]["consumer_id"] = str(consumer_id)
        if provider_id:
            session["context"]["provider_id"] = str(provider_id)
        if enrollment_id:
            session["context"]["enrollment_id"] = str(enrollment_id)
        
        # Handle workflow actions
        if action:
            return await self._handle_action(session_id, session, action)
        
        # Store and process media if provided
        stored_media = []
        if media:
            is_valid, error = media_service.validate_attachments(media)
            if not is_valid:
                return session_id, f"Sorry, there was an issue with your media: {error}", None, None, False
            
            stored_media = media_service.store_attachments(media, session_id)
            session["context"]["media"].extend(stored_media)
        
        if self.is_mock:
            response_text, data = self._mock_response(message, role, session["context"], stored_media)
            return session_id, response_text, data, session["context"].get("draft"), session["context"].get("awaiting_approval", False)
        
        try:
            chat = session["chat"]
            
            # Build message parts
            parts = []
            
            # Add context prefix
            context_prefix = f"[User role: {role}]"
            if provider_id:
                context_prefix += f" [Provider ID: {provider_id}]"
            
            # Add media to message
            if stored_media:
                for sm in stored_media:
                    try:
                        media_data = media_service.prepare_for_gemini(sm)
                        parts.append({
                            "inline_data": {
                                "mime_type": media_data["mime_type"],
                                "data": media_data["data"]
                            }
                        })
                    except Exception as e:
                        logger.error(f"Failed to prepare media for Gemini: {e}")
            
            # Add text message
            if message:
                parts.append(f"{context_prefix}\n\nUser: {message}")
            elif stored_media:
                parts.append(f"{context_prefix}\n\nUser shared {len(stored_media)} {'photo' if len(stored_media) == 1 else 'photos'}.")
            
            # Send message and get response
            response = chat.send_message(parts)
            
            structured_data = None
            
            # Handle function calls
            while response.candidates and response.candidates[0].content.parts:
                function_call = None
                text_parts = []
                
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call.name:
                        function_call = part.function_call
                        break
                    elif hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                
                if not function_call:
                    break
                
                # Execute the function
                function_name = function_call.name
                function_args = dict(function_call.args)
                
                logger.info(f"Executing function: {function_name} with args: {function_args}")
                
                result = self._execute_tool(function_name, function_args, session["context"])
                
                # Capture structured data
                structured_data = self._capture_structured_data(function_name, result, structured_data)
                
                # Send function result back
                function_response = genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=function_name,
                        response={"result": json.dumps(result)}
                    )
                )
                
                response = chat.send_message(function_response)
            
            # Extract final text response
            response_text = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
            
            # Consult Specialist if relevant
            await self._consult_specialist(session["context"], message, response_text, stored_media)
            
            # Check if response indicates a draft
            draft = self._detect_draft_in_response(response_text, session["context"])
            awaiting_approval = draft is not None
            
            if draft:
                session["context"]["draft"] = draft
                session["context"]["awaiting_approval"] = True
            
            return session_id, response_text, structured_data, draft, awaiting_approval
            
        except Exception as e:
            logger.error(f"Error in handle_chat: {str(e)}")
            return session_id, "I'm sorry, I'm having trouble processing that right now. Could you try again?", None, None, False

    async def _handle_action(
        self, 
        session_id: str, 
        session: Dict, 
        action: str
    ) -> Tuple[str, str, Optional[Dict], Optional[DraftRequest], bool]:
        """Handle workflow actions (approve, edit, cancel)."""
        context = session["context"]
        draft = context.get("draft")
        
        if action == "approve_request":
            if not draft:
                return session_id, "There's no draft request to approve. Let me help you create one!", None, None, False
            
            # Create the actual service request
            try:
                result = self._execute_tool(
                    "create_service_request",
                    {
                        "service_type": draft.service_type,
                        "description": draft.description,
                        "city": draft.location.get("city", ""),
                        "budget_min": draft.budget.get("min", 0),
                        "budget_max": draft.budget.get("max", 100),
                        "timing": draft.timing or "",
                        "media": [m.dict() for m in draft.media],
                    },
                    context
                )
                
                # Clear draft
                context["draft"] = None
                context["awaiting_approval"] = False
                
                return (
                    session_id, 
                    f"Done! ✅ Your request has been posted! I'll notify you as soon as stylists respond. Based on your criteria, you should hear back within a few hours!",
                    {"request_id": result.get("request_id")},
                    None,
                    False
                )
            except Exception as e:
                logger.error(f"Failed to create request: {e}")
                return session_id, f"Sorry, there was an error posting your request: {str(e)}", None, draft, True
        
        elif action == "edit_request":
            context["draft"] = None
            context["awaiting_approval"] = False
            return session_id, "No problem! What would you like to change?", None, None, False
        
        elif action == "cancel_request":
            context["draft"] = None
            context["awaiting_approval"] = False
            context["gathered_info"] = {}
            context["media"] = []
            context["media_descriptions"] = []
            return session_id, "Request cancelled. Is there something else I can help you with?", None, None, False
        
        return session_id, "I didn't understand that action.", None, context.get("draft"), context.get("awaiting_approval", False)

    async def _consult_specialist(self, context: Dict, user_message: Optional[str], assistant_message: str, stored_media: List[StoredMedia]):
        """Consult a specialist agent to analyze the current state of the request."""
        # Try to find a specialist for the current service type
        service_type = context.get("gathered_info", {}).get("service_type")
        if not service_type:
            # Try to infer from message
            combined_text = (user_message or "") + " " + assistant_message
            specialist = specialist_registry.find_for_service(combined_text)
        else:
            specialist = specialist_registry.find_for_service(service_type)
            
        if not specialist:
            return

        # Prepare context for specialist
        info = context.get("gathered_info", {})
        
        # In a real scenario, we'd have vision AI descriptions already.
        # For now, let's assume the assistant_message contains some analysis or we rely on Gemini's vision.
        media_descriptions = context.get("media_descriptions", [])
        
        # Analyze
        analysis = await specialist.analyze(
            service_type=service_type or "unknown",
            description=info.get("description", user_message or ""),
            location=info.get("location", {}),
            budget=info.get("budget", {}),
            timing=info.get("timing"),
            media_descriptions=media_descriptions,
            additional_context={"assistant_message": assistant_message}
        )
        
        # Store specialist feedback
        context["specialist_analysis"] = analysis
        
        # Update gathered info with enriched data
        if analysis.enriched_data:
            info.update(analysis.enriched_data)
            context["gathered_info"] = info

    def _detect_draft_in_response(self, response_text: str, context: Dict) -> Optional[DraftRequest]:
        """Detect if the response contains a draft request summary."""
        # Look for draft-like patterns
        lower = response_text.lower()
        if any(phrase in lower for phrase in [
            "here's your request",
            "request summary",
            "would you like to post",
            "ready to post",
            "shall i post"
        ]):
            # Try to create a draft from gathered info + specialist analysis
            info = context.get("gathered_info", {})
            analysis = context.get("specialist_analysis")
            
            if info:
                # Merge media
                media = context.get("media", [])
                
                return DraftRequest(
                    service_type=info.get("service_type") or info.get("service_subtype") or "Service",
                    service_category="hair" if "hair" in lower else "general",
                    description=info.get("description", ""),
                    details={k: v for k, v in info.items() if k not in ["service_type", "service_subtype", "description", "location", "budget", "timing"]},
                    location=info.get("location", {"city": "Unknown"}),
                    budget=info.get("budget", {"min": 0, "max": 100}),
                    timing=info.get("timing"),
                    media=media,
                    specialist_notes=analysis.notes if analysis else None
                )
        return None

    def _execute_tool(self, name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool/function and return results."""
        try:
            if name == "create_service_request":
                consumer_id = context.get("consumer_id") or str(uuid4())
                context["consumer_id"] = consumer_id
                
                # Build description with extra details
                description = params.get("description", params.get("service_type", ""))
                if params.get("hair_type"):
                    description += f" Hair type: {params['hair_type']}."
                if params.get("style_preferences"):
                    description += f" Style: {params['style_preferences']}."
                
                result = handlers.create_service_request(
                    consumer_id=UUID(consumer_id),
                    service_category=params.get("service_type", "general"),
                    service_type=params.get("service_type", ""),
                    raw_input=description,
                    requirements={},
                    location={"city": params.get("city", "")},
                    timing={"urgency": "flexible", "preference": params.get("timing", "")},
                    budget={"min": params.get("budget_min", 0), "max": params.get("budget_max", 100)},
                    media=params.get("media", [])
                )
                
                if "request_id" in result:
                    context["current_request_id"] = result["request_id"]
                
                return result
                
            elif name == "get_offers":
                request_id = params.get("request_id") or context.get("current_request_id")
                if request_id:
                    result = handlers.get_offers(UUID(request_id))
                    context["current_offers"] = result.get("offers", [])
                    return result
                return {"error": "No request ID available"}
                
            elif name == "accept_offer":
                return handlers.accept_offer(
                    offer_id=UUID(params["offer_id"]),
                    selected_slot={
                        "date": params["slot_date"],
                        "start_time": params["slot_start_time"]
                    }
                )
                
            elif name == "get_service_catalog":
                from src.platform.services.catalog import catalog_service
                # Return full categories with services for the UI selector
                return {"categories": catalog_service.catalog.get("categories", [])}

            elif name == "update_enrollment":
                enrollment_id = context.get("enrollment_id")
                if not enrollment_id:
                    return {"error": "No enrollment session active"}
                
                from src.platform.database import SessionLocal
                from src.platform.models.provider import ProviderEnrollment
                with SessionLocal() as db:
                    enrollment = db.query(ProviderEnrollment).filter(ProviderEnrollment.id == UUID(enrollment_id)).first()
                    if enrollment:
                        current_data = enrollment.data or {}
                        current_data.update(params)
                        enrollment.data = current_data
                        db.commit()
                        return {"status": "success", "updated_fields": list(params.keys())}
                return {"error": "Enrollment not found"}

            elif name == "get_enrollment_summary":
                enrollment_id = context.get("enrollment_id")
                if not enrollment_id:
                    return {"error": "No enrollment session active"}
                
                from src.platform.database import SessionLocal
                from src.platform.models.provider import ProviderEnrollment
                with SessionLocal() as db:
                    enrollment = db.query(ProviderEnrollment).filter(ProviderEnrollment.id == UUID(enrollment_id)).first()
                    if enrollment:
                        return enrollment.data
                return {"error": "Enrollment not found"}

            elif name == "request_portfolio":
                return {"show_portfolio": True}

            elif name == "submit_enrollment":
                enrollment_id = context.get("enrollment_id")
                if not enrollment_id:
                    return {"error": "No enrollment session active"}
                
                from src.platform.database import SessionLocal
                from src.platform.models.provider import ProviderEnrollment
                from src.platform.services.verification import verification_service
                with SessionLocal() as db:
                    enrollment = db.query(ProviderEnrollment).filter(ProviderEnrollment.id == UUID(enrollment_id)).first()
                    if enrollment:
                        enrollment.status = "pending"
                        db.commit()
                        return verification_service.process_enrollment(enrollment, db)
                return {"error": "Enrollment not found"}

            elif name == "get_my_leads":
                provider_id = params.get("provider_id") or context.get("provider_id")
                if provider_id:
                    return handlers.get_matching_requests(UUID(provider_id))
                return {"error": "No provider ID available"}
                
            elif name == "get_lead_details":
                request_id = params.get("request_id")
                provider_id = context.get("provider_id")
                if request_id:
                    # Mark as viewed if provider is known
                    if provider_id:
                        handlers.mark_lead_viewed(UUID(provider_id), UUID(request_id))
                    
                    # Get request with all details
                    from src.platform.database import SessionLocal
                    from src.platform.models.request import ServiceRequest
                    with SessionLocal() as db:
                        req = db.query(ServiceRequest).filter(ServiceRequest.id == UUID(request_id)).first()
                        if req:
                            return {
                                "id": str(req.id),
                                "service_type": req.service_type,
                                "raw_input": req.raw_input,
                                "location": req.location,
                                "budget": req.budget,
                                "timing": req.timing,
                                "media": req.media,
                                "specialist_analysis": req.requirements.get("specialist_analysis") if req.requirements else None
                            }
                return {"error": "Request not found"}

            elif name == "suggest_offer":
                request_id = params.get("request_id")
                provider_id = params.get("provider_id") or context.get("provider_id")
                if request_id and provider_id:
                    # Fetch req and provider data
                    from src.platform.database import SessionLocal
                    from src.platform.models.request import ServiceRequest
                    with SessionLocal() as db:
                        req = db.query(ServiceRequest).filter(ServiceRequest.id == UUID(request_id)).first()
                        provider = handlers.get_provider(UUID(provider_id))
                        
                        if req and provider:
                            # Convert to dict
                            req_dict = {
                                "service_type": req.service_type,
                                "budget": req.budget,
                                "specialist_analysis": req.requirements.get("specialist_analysis") if req.requirements else {}
                            }
                            # Wrap in async call (we are in sync thread here usually, or need await)
                            # For simplicity since suggester is sync-like for now:
                            import asyncio
                            loop = asyncio.new_event_loop()
                            suggestion = loop.run_until_complete(suggestion_service.suggest_offer(req_dict, provider))
                            loop.close()
                            return suggestion.dict()
                return {"error": "Could not generate suggestion"}

            elif name == "draft_offer":
                # Create a draft offer for UI review
                draft = {
                    "id": str(uuid4()),
                    "request_id": params.get("request_id"),
                    "price": params.get("price"),
                    "date": params.get("date"),
                    "time": params.get("time"),
                    "message": params.get("message")
                }
                context["offer_draft"] = draft
                return draft

            elif name == "submit_offer":
                # Final submission using either draft or direct params
                draft = context.get("offer_draft")
                
                request_id = params.get("request_id") or (draft.get("request_id") if draft else None)
                provider_id = params.get("provider_id") or context.get("provider_id")
                price = params.get("price") or (draft.get("price") if draft else None)
                date = params.get("date") or (draft.get("date") if draft else None)
                time = params.get("time") or (draft.get("time") if draft else None)
                message = params.get("message") or (draft.get("message") if draft else "")

                if not request_id or not provider_id or not price:
                    return {"error": "Missing required fields for offer"}

                return handlers.submit_offer(
                    request_id=UUID(request_id),
                    provider_id=UUID(provider_id),
                    price=price,
                    available_slots=[{
                        "date": date,
                        "start_time": time,
                        "end_time": time # Simplified for MVP
                    }],
                    message=message
                )
            
            return {"error": f"Unknown function: {name}"}
            
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return {"error": str(e)}

    def _capture_structured_data(
        self, 
        function_name: str, 
        result: Dict[str, Any],
        existing_data: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Capture structured data from function results."""
        data = existing_data or {}
        
        if function_name == "get_offers":
            data["offers"] = result.get("offers", [])
        elif function_name == "create_service_request":
            data["request_id"] = result.get("request_id")
        elif function_name == "accept_offer" and "booking_id" in result:
            data["booking"] = result
        elif function_name == "get_matching_requests" or function_name == "get_my_leads":
            data["requests"] = result if isinstance(result, list) else result.get("requests", [])
        elif function_name == "get_lead_details":
            data["lead"] = result
        elif function_name == "suggest_offer":
            data["suggestion"] = result
        elif function_name == "get_service_catalog":
            data["categories"] = result.get("categories", [])
        elif function_name == "update_enrollment":
            # We don't necessarily need to return data to FE here, 
            # unless we want to show a 'saved' indicator.
            data["enrollment_updated"] = True
        elif function_name == "get_enrollment_summary":
            data["enrollment_summary"] = result
        elif function_name == "request_portfolio":
            data["show_portfolio"] = True
        elif function_name == "submit_enrollment":
            data["enrollment_result"] = result
        
        return data if data else None

    def _mock_response(
        self, 
        message: Optional[str], 
        role: str, 
        context: Dict[str, Any],
        media: List[StoredMedia]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Generate mock responses for testing."""
        m = (message or "").lower()
        
        # If media was shared
        if media:
            media_type = media[0].type
            if media_type == "image":
                return (
                    "I can see your photo! 📷 It looks like you have beautiful curly hair, about shoulder-length. "
                    "I notice some natural highlights too. What kind of style are you thinking?",
                    None
                )
            elif media_type == "video":
                return "Thanks for the video! I can see your hair from different angles. What would you like to do with it?", None
        
        # Draft approval simulation
        if context.get("awaiting_approval"):
            if "yes" in m or "post" in m or "approve" in m:
                context["awaiting_approval"] = False
                context["draft"] = None
                return "Done! ✅ Your request has been posted! I'll notify you as soon as stylists respond.", {
                    "request_id": str(uuid4())
                }
        
        if "haircut" in m:
            return (
                "I'd love to help you find a great stylist! 💇 Could you show me your current hair? "
                "You can take a photo or upload one using the + button.",
                None
            )
        
        if "brooklyn" in m and ("60" in m or "70" in m or "80" in m):
            # Create a mock draft
            draft = DraftRequest(
                service_type="Haircut",
                service_category="hair",
                description="Looking for a haircut",
                details={"style": "curly bob"},
                location={"city": "Brooklyn"},
                budget={"min": 60, "max": 80},
                timing="This weekend",
                media=[],
                specialist_notes="Type 3B curly hair identified"
            )
            context["draft"] = draft
            context["awaiting_approval"] = True
            
            return (
                "Here's your request summary:\n\n"
                "📋 **Service**: Haircut\n"
                "💇 **Details**: Curly bob, maintaining curl pattern\n"
                "📍 **Location**: Brooklyn\n"
                "💰 **Budget**: $60-80\n"
                "📅 **Timing**: This weekend\n\n"
                "Would you like to post this request?",
                None
            )
        
        if role == "provider" and ("lead" in m or "request" in m):
            return "Here are the new leads matching your skills:", {
                "requests": [{
                    "request_id": str(uuid4()),
                    "service_type": "Haircut",
                    "location": {"city": "Brooklyn"},
                    "budget": {"min": 60, "max": 100},
                    "raw_input": "I need a haircut for curly hair"
                }]
            }

        if role == "consumer":
            return "Hi! I'm Proxie, your personal concierge. 👋 What service can I help you find today?", None
        else:
            return "Hi! I'm Proxie. Ready to help you manage your business. 📋 Would you like to see your new leads?", None


# Global service instance
chat_service = ChatService()
