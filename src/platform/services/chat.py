"""
Proxie Chat Service - Gemini Integration with Multi-Modal Support

Handles conversational AI interactions using Google's Gemini API,
including image/video understanding and specialist consultation.
"""

import json
import base64
import structlog
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4

from src.platform.config import settings
from src.mcp import handlers
from src.platform.schemas.media import MediaAttachment, StoredMedia
from src.platform.schemas.chat import DraftRequest
from src.platform.services.media import media_service
from src.platform.services.specialists import specialist_registry
from src.platform.services.suggestions import suggestion_service
from src.platform.services.llm_gateway import llm_gateway

logger = structlog.get_logger(__name__)

CONSUMER_SYSTEM_PROMPT = """You are the Proxie Consumer Agent, a premium concierge for users looking for high-quality services.

Your goal: Orchestrate a seamless, high-end experience that feels like chatting with a personal assistant.

Account Creation & Personalization:
- If 'consumer_id' is present but 'name' or 'default_location' are missing, your first priority is to gather this info naturally.
- ALWAYS use the user's name if available in {consumer_profile}.
- If you just updated their profile, proactively suggest they "Secure their profile" to keep their preferences safe.

Rich Interaction Rules:
- Proactive Assistance: Don't just answer; guide. For example, "I've analyzed your photo! It looks like you're looking for a fade. Would you like me to find stylists who specialize in that?"
- Rich UI Elements: You can use special tags to trigger frontend widgets:
  - Mentioning "I'm showing you the service catalog" will trigger the visual selector.
  - Mentioning "Let's pick a time" will trigger the calendar picker.
  - Use [button: Text | action] for quick shortcuts, e.g., [button: Approve Draft | approve_request].

Conversational Style:
- Professional yet warm. Use emojis sparingly for personality.
- Be concise. One step at a time.
- If the user shares a photo, acknowledge what you see in it immediately.

Capabilities:
- Analyze photos to identify hair types or service needs.
- Prepare draft requests and ask for approval.
- Post requests to the live marketplace via 'create_service_request'.
- List and help select provider offers via 'get_offers' and 'accept_offer'.
- Get and update user profile info via 'get_consumer_profile' and 'update_consumer_profile'.
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
3. Select services from the catalog using 'get_service_catalog'. 
   IMPORTANT: If the provider has already mentioned their profession (e.g. "hairstylist", "plumber", "cleaner"), 
   DO NOT show all categories. Only show the relevant category and its services.
   For example, if they said "I'm a hairstylist", only show Hair & Beauty services, not Cleaning/Plumbing/etc.
4. Set pricing and duration for each service.
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
- NEVER show unrelated service categories. If someone is a hairstylist, only show hair-related services.
"""

# Keep general prompt as fallback
SYSTEM_PROMPT = CONSUMER_SYSTEM_PROMPT

# Tool definitions
ENROLLMENT_TOOL_DECLARATIONS = [
    {
        "name": "get_service_catalog",
        "description": "Get the list of service categories and services available on the platform. Use category_filter to show only relevant categories based on what the provider has said about their profession.",
        "parameters": {
            "type": "object",
            "properties": {
                "category_filter": {
                    "type": "string",
                    "description": "Optional. Filter to show only a specific category (e.g., 'hair', 'cleaning', 'plumbing'). If the provider said 'I'm a hairstylist', use 'hair' to only show Hair & Beauty services."
                }
            }
        }
    },
    {
        "name": "update_enrollment",
        "description": "Update provider enrollment data (profile, location, services, etc.) as it's collected.",
        "parameters": {
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
    },
    {
        "name": "get_enrollment_summary",
        "description": "Get the current enrollment summary for review.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "request_portfolio",
        "description": "Trigger the portfolio upload interface for the provider.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "submit_enrollment",
        "description": "Finalize and submit the enrollment for verification. Only call after user review.",
        "parameters": {"type": "object", "properties": {}}
    }
]

TOOL_DECLARATIONS = [
    {
        "name": "create_service_request",
        "description": "Create a service request AFTER user has approved the draft. This posts the request to find providers.",
        "parameters": {
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
    },
    {
        "name": "get_offers",
        "description": "Get offers from providers for a service request",
        "parameters": {
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "description": "The service request ID"}
            },
            "required": ["request_id"]
        }
    },
    {
        "name": "accept_offer",
        "description": "Accept an offer and create a confirmed booking. Only call after user explicitly confirms.",
        "parameters": {
            "type": "object",
            "properties": {
                "offer_id": {"type": "string", "description": "The offer ID to accept"},
                "slot_date": {"type": "string", "description": "Selected date in YYYY-MM-DD format"},
                "slot_start_time": {"type": "string", "description": "Selected time in HH:MM format"}
            },
            "required": ["offer_id", "slot_date", "slot_start_time"]
        }
    },
    {
        "name": "get_my_leads",
        "description": "List all new and matching service requests for a provider.",
        "parameters": {
            "type": "object",
            "properties": {
                "provider_id": {"type": "string", "description": "The provider ID"}
            },
            "required": ["provider_id"]
        }
    },
    {
        "name": "get_lead_details",
        "description": "Get full details for a specific lead, including consumer photos, descriptions, and specialist analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "description": "The lead/request ID"}
            },
            "required": ["request_id"]
        }
    },
    {
        "name": "suggest_offer",
        "description": "Get AI suggestions for pricing, timing, and response message for a specific lead.",
        "parameters": {
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "description": "The lead ID"},
                "provider_id": {"type": "string", "description": "The provider ID"}
            },
            "required": ["request_id", "provider_id"]
        }
    },
    {
        "name": "draft_offer",
        "description": "Draft an offer for provider review. Use after 'suggest_offer' or when provider gives price/time.",
        "parameters": {
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
    },
    {
        "name": "submit_offer",
        "description": "Final submit of an offer AFTER provider has approved the draft.",
        "parameters": {
            "type": "object",
            "properties": {
                "draft_id": {"type": "string", "description": "The ID of the approved draft"}
            },
            "required": ["draft_id"]
        }
    },
    {
        "name": "get_consumer_profile",
        "description": "Get the consumer's profile information, including their default location and preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "consumer_id": {"type": "string", "description": "The consumer ID"}
            },
            "required": ["consumer_id"]
        }
    },
    {
        "name": "update_consumer_profile",
        "description": "Update the consumer's profile information, such as name, email, phone, or default location.",
        "parameters": {
            "type": "object",
            "properties": {
                "consumer_id": {"type": "string", "description": "The consumer ID"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "default_location": {"type": "object", "description": "Location info: {city, state, zip, address, lat, lng}"}
            },
            "required": ["consumer_id"]
        }
    }
]

# Import session manager
from src.platform.sessions import session_manager

# sessions: Dict[str, Dict[str, Any]] = {} - REPLACED BY REDIS


class ChatService:
    def __init__(self):
        self.is_mock = self._is_mock_mode()
        # genai configuration removed, using llm_gateway

    def _is_mock_mode(self) -> bool:
        return not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY in ["", "your-gemini-api-key", "your-key-here"]

    def _get_model_params(self, role: str, provider_id: Optional[UUID] = None) -> Tuple[str, List[Dict]]:
        """Get specialized model parameters based on role."""
        prompt = CONSUMER_SYSTEM_PROMPT
        tools = self._get_openai_tools(TOOL_DECLARATIONS)
        
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
            tools = self._get_openai_tools(ENROLLMENT_TOOL_DECLARATIONS)
            
        return prompt, tools

    def _get_openai_tools(self, functions: List) -> List[Dict]:
        """Convert custom/Gemini function declarations to OpenAI tool format."""
        openai_tools = []
        for fn in functions:
            # Handle both list of dicts and list of objects
            if hasattr(fn, 'to_dict'):
                fn_dict = fn.to_dict()
            elif isinstance(fn, dict):
                fn_dict = fn
            else:
                # Fallback for unexpected types
                fn_dict = {
                    "name": getattr(fn, 'name', 'unnamed'),
                    "description": getattr(fn, 'description', ''),
                    "parameters": getattr(fn, 'parameters', {"type": "object", "properties": {}})
                }

            openai_tools.append({
                "type": "function",
                "function": {
                    "name": fn_dict["name"],
                    "description": fn_dict["description"],
                    "parameters": fn_dict["parameters"]
                }
            })
        return openai_tools

    def _get_or_create_session(self, session_id: Optional[str], role: str, provider_id: Optional[UUID]) -> Tuple[str, Dict]:
        """Get existing session or create a new one."""
        if not session_id:
            session_id = str(uuid4())
        
        session = session_manager.get_session(session_id)
        if not session:
            system_prompt, tools = self._get_model_params(role, provider_id)
            session = {
                "messages": [{"role": "system", "content": system_prompt}],
                "tools": tools,
                "context": {
                    "role": role,
                    "provider_id": str(provider_id) if provider_id else None,
                    "current_request_id": None,
                    "current_offers": [],
                    "gathered_info": {},
                    "media": [],
                    "media_descriptions": [],
                    "draft": None,
                    "awaiting_approval": False,
                },
                "specialist_feedback": None,
            }
            session_manager.save_session(session_id, session)
        
        return session_id, session

    async def handle_chat(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        role: str = "consumer",
        consumer_id: Optional[str] = None,
        provider_id: Optional[str] = None,
        enrollment_id: Optional[str] = None,
        media: List[ChatMedia] = None,
        action: Optional[str] = None,
        clerk_id: Optional[str] = None
    ) -> Tuple[str, str, Optional[Dict], Optional[DraftRequest], bool]:
        """
        Main entry point for handling a chat message.
        """
        # Load or create session
        session_id, session = self._get_or_create_session(session_id, role, provider_id) # Keep original order for now
        
        # Hydrate context
        session["context"]["role"] = role
        session["context"]["consumer_id"] = consumer_id
        session["context"]["provider_id"] = provider_id
        session["context"]["enrollment_id"] = enrollment_id
        session["context"]["clerk_id"] = clerk_id  # Store clerk_id in context
        
        if clerk_id:
            # Load consumer profile using clerk_id
            from src.platform.database import SessionLocal
            from src.platform.models.consumer import Consumer
            with SessionLocal() as db:
                consumer = db.query(Consumer).filter(Consumer.clerk_id == clerk_id).first()
                if consumer:
                    session["context"]["consumer_profile"] = consumer.to_dict()
                else:
                    # Create a default profile if not exists
                    consumer = Consumer(clerk_id=clerk_id)
                    db.add(consumer)
                    db.commit()
                    db.refresh(consumer)
                    session["context"]["consumer_profile"] = consumer.to_dict()
        elif consumer_id:
            # Fallback to consumer_id if clerk_id not provided
            from src.platform.database import SessionLocal
            from src.platform.models.consumer import Consumer
            with SessionLocal() as db:
                consumer = db.query(Consumer).filter(Consumer.id == UUID(str(consumer_id))).first()
                if consumer:
                    session["context"]["consumer_profile"] = consumer.to_dict()
                else:
                    # Create a default profile if not exists
                    consumer = Consumer(id=UUID(str(consumer_id)))
                    db.add(consumer)
                    db.commit()
                    db.refresh(consumer)
                    session["context"]["consumer_profile"] = consumer.to_dict()
        if provider_id:
            session["context"]["provider_id"] = str(provider_id)
        if enrollment_id:
            session["context"]["enrollment_id"] = str(enrollment_id)
        
        # Handle workflow actions
        if action:
            return await self._handle_action(session_id, session, action)
            
        # Smart Greeting: If brand new session and we have a name, say hi!
        # Detect if it's the first real message in the session
        is_first_message = len(session.get("messages", [])) <= 1 # System prompt + maybe one message
        if is_first_message and not message and not media:
            profile = session["context"].get("consumer_profile", {})
            name = profile.get("name")
            if name:
                return session_id, f"Welcome back, {name.split()[0]}! 👋 How can I help you today?", None, None, False
        
        # Store and process media if provided
        stored_media = []
        if media:
            is_valid, error = media_service.validate_attachments(media)
            if not is_valid:
                return session_id, f"Sorry, there was an issue with your media: {error}", None, None, False
            
            stored_media = media_service.store_attachments(media, session_id)
            session["context"]["media"].extend([m.dict() for m in stored_media])
            
            # Trigger background analysis
            try:
                from src.platform.worker import celery_app
                celery_app.send_task("analyze_session_media", args=[session_id])
            except Exception as e:
                logger.error(f"Failed to trigger background analysis: {e}")
        
        if self.is_mock:
            response_text, data = self._mock_response(message, role, session["context"], stored_media)
            return session_id, response_text, data, session["context"].get("draft"), session["context"].get("awaiting_approval", False)
        
        try:
            # Build user message content
            content_list = []
            
            context_prefix = f"[User role: {role}]"
            if provider_id:
                context_prefix += f" [Provider ID: {provider_id}]"
            
            # Prepare media
            if stored_media:
                for sm in stored_media:
                    try:
                        media_data = media_service.prepare_for_gemini(sm)
                        content_list.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_data['mime_type']};base64,{media_data['data']}"
                            }
                        })
                    except Exception as e:
                        logger.error(f"Failed to prepare media: {e}")
            
            # Prepare text
            user_text = ""
            if message:
                user_text = f"{context_prefix}\n\nUser: {message}"
            elif stored_media:
                user_text = f"{context_prefix}\n\nUser shared {len(stored_media)} photos."
            
            if user_text:
                content_list.append({"type": "text", "text": user_text})
            
            # Setup System Prompt based on role
            system_prompt = ""
            if role == "consumer":
                profile = session["context"].get("consumer_profile", {})
                system_prompt = CONSUMER_SYSTEM_PROMPT.format(consumer_profile=json.dumps(profile))
            elif role == "provider":
                # Assuming provider name is something we have or can get
                provider_name = session["context"].get("provider_name", "Provider")
                system_prompt = PROVIDER_SYSTEM_PROMPT.format(provider_name=provider_name)
            elif role == "enrollment":
                system_prompt = ENROLLMENT_SYSTEM_PROMPT
            else:
                system_prompt = CONSUMER_SYSTEM_PROMPT.format(consumer_profile="{}")

            # Add System Prompt at the beginning of sessions if not present
            if not session["messages"] or session["messages"][0]["role"] != "system":
                session["messages"].insert(0, {"role": "system", "content": system_prompt})
            
            # Add to session messages
            session["messages"].append({"role": "user", "content": content_list})
            
            response_text = ""
            structured_data = None
            
            # Process with LLM (allowing for tool calls)
            for _ in range(5):  # Max 5 internal turns
                response = await llm_gateway.chat_completion(
                    messages=session["messages"],
                    tools=session["tools"],
                    user_id=clerk_id,
                    session_id=session_id,
                    feature=f"chat_{role}"
                )
                
                ai_message = response.choices[0].message
                # Store message for history
                session["messages"].append(ai_message.to_dict())
                
                if ai_message.content:
                    response_text += ai_message.content
                
                if not ai_message.tool_calls:
                    break
                
                # Process tool calls
                for tool_call in ai_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Executing tool: {function_name}", args=function_args)
                    result = self._execute_tool(function_name, function_args, session["context"])
                    
                    # Capture structured data
                    structured_data = self._capture_structured_data(function_name, result, structured_data)
                    
                    # Add tool response to history
                    session["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(result)
                    })
            
            # Consult Specialist if relevant
            await self._consult_specialist(session["context"], message, response_text, stored_media)
            
            # Check if response indicates a draft
            draft = self._detect_draft_in_response(response_text, session["context"])
            awaiting_approval = draft is not None
            
            if draft:
                session["context"]["draft"] = draft.dict() if hasattr(draft, 'dict') else draft
                session["context"]["awaiting_approval"] = True
            
            # Parse UI hints and buttons from final response
            structured_data = self._parse_ui_elements(response_text, structured_data)
            
            # Save session to Redis
            session_manager.save_session(session_id, session)
            
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
                
                session_manager.save_session(session_id, session)
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
            session_manager.save_session(session_id, session)
            return session_id, "No problem! What would you like to change?", None, None, False
        
        elif action == "cancel_request":
            context["draft"] = None
            context["awaiting_approval"] = False
            context["gathered_info"] = {}
            context["media"] = []
            context["media_descriptions"] = []
            session_manager.save_session(session_id, session)
            return session_id, "Request cancelled. Is there something else I can help you with?", None, None, False
        
        session_manager.save_session(session_id, session)
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
        from dataclasses import asdict
        context["specialist_analysis"] = asdict(analysis) if hasattr(analysis, '__dataclass_fields__') else analysis
        
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
                # Resolve Internal UUID for database
                # Prefer UUID from profile (linked via clerk_id earlier in handle_chat)
                internal_id = None
                profile = context.get("consumer_profile", {})
                if profile.get("id"):
                    internal_id = UUID(str(profile["id"]))
                else:
                    # Fallback to provided consumer_id if it's a valid UUID
                    # (e.g. for guest/unauthenticated sessions if allowed)
                    cid_raw = context.get("consumer_id")
                    if cid_raw:
                        try:
                            internal_id = UUID(str(cid_raw))
                        except ValueError:
                            # Not a UUID, likely a clerk_id that hasn't synced profile yet
                            pass
                
                if not internal_id:
                     # Create a default UUID if everything else fails
                     internal_id = uuid.uuid4()
                
                # Update context so subsequent tool calls use the same internal identity
                context["consumer_id"] = str(internal_id)
                
                # Build description with extra details
                description = params.get("description", params.get("service_type", ""))
                if params.get("hair_type"):
                    description += f" Hair type: {params['hair_type']}."
                if params.get("style_preferences"):
                    description += f" Style: {params['style_preferences']}."
                
                # Use consumer profile location if city is missing from tool call
                city = params.get("city")
                if not city:
                    city = profile.get("default_location", {}).get("city", "Unknown")
                
                result = handlers.create_service_request(
                    consumer_id=internal_id,
                    service_category=params.get("service_type", "general"),
                    service_type=params.get("service_type", ""),
                    raw_input=description,
                    requirements={},
                    location={"city": city},
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
                all_categories = catalog_service.catalog.get("categories", [])
                
                # Apply category filter if provided
                category_filter = params.get("category_filter", "").lower() if params else ""
                if category_filter:
                    # Filter categories based on the filter term
                    filter_mappings = {
                        "hair": ["hair & beauty", "hair and beauty", "beauty", "salon"],
                        "cleaning": ["cleaning", "home cleaning", "housekeeping"],
                        "plumbing": ["plumbing", "home repair", "handyman"],
                        "electrical": ["electrical", "home repair", "handyman"],
                        "photography": ["photography", "media", "creative"],
                    }
                    
                    # Find matching category names
                    matching_names = filter_mappings.get(category_filter, [category_filter])
                    filtered_categories = [
                        cat for cat in all_categories 
                        if any(match in cat.get("name", "").lower() for match in matching_names)
                    ]
                    
                    if filtered_categories:
                        return {"categories": filtered_categories}
                
                # Return all categories if no filter or no match
                return {"categories": all_categories}

            elif name == "get_consumer_profile":
                clerk_id = context.get("clerk_id")
                consumer_id = params.get("consumer_id") or context.get("consumer_id")
                
                from src.platform.database import SessionLocal
                from src.platform.models.consumer import Consumer
                with SessionLocal() as db:
                    # Prefer clerk_id lookup for security
                    if clerk_id:
                        consumer = db.query(Consumer).filter(Consumer.clerk_id == clerk_id).first()
                    elif consumer_id:
                        consumer = db.query(Consumer).filter(Consumer.id == UUID(str(consumer_id))).first()
                    else:
                        return {"error": "No identity available"}
                        
                    if consumer:
                        return consumer.to_dict()
                return {"error": "Consumer not found"}

            elif name == "update_consumer_profile":
                clerk_id = context.get("clerk_id")
                consumer_id = params.get("consumer_id") or context.get("consumer_id")
                
                from src.platform.database import SessionLocal
                from src.platform.models.consumer import Consumer
                with SessionLocal() as db:
                    # Resolve consumer by clerk_id or internal ID
                    consumer = None
                    if clerk_id:
                        consumer = db.query(Consumer).filter(Consumer.clerk_id == clerk_id).first()
                    elif consumer_id:
                        consumer = db.query(Consumer).filter(Consumer.id == UUID(str(consumer_id))).first()
                    
                    if not consumer:
                        # Auto-create profile if authenticated via Clerk
                        if clerk_id:
                            consumer = Consumer(clerk_id=clerk_id)
                            db.add(consumer)
                        else:
                            return {"error": "No identity available to create profile"}
                    
                    # Update allowed fields
                    fields = ["name", "email", "phone", "default_location", "preferences"]
                    for field in fields:
                        if field in params:
                            setattr(consumer, field, params[field])
                    
                    db.commit()
                    db.refresh(consumer)
                    # Update context with new data
                    context["consumer_profile"] = consumer.to_dict()
                    return consumer.to_dict()


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
            data["ui_hint"] = "compare_offers"
        elif function_name == "get_consumer_profile" or function_name == "update_consumer_profile":
            data["consumer_profile"] = result
        elif function_name == "create_service_request":
            data["request_id"] = result.get("request_id")
            data["ui_hint"] = "request_created"
        elif function_name == "accept_offer" and "booking_id" in result:
            data["booking"] = result
            data["ui_hint"] = "booking_confirmed"
        elif function_name == "get_matching_requests" or function_name == "get_my_leads":
            data["requests"] = result if isinstance(result, list) else result.get("requests", [])
            data["ui_hint"] = "show_leads"
        elif function_name == "get_lead_details":
            data["lead"] = result
        elif function_name == "suggest_offer":
            data["suggestion"] = result
            data["ui_hint"] = "offer_helper"
        elif function_name == "get_service_catalog":
            data["categories"] = result.get("categories", [])
            data["ui_hint"] = "service_selector"
        elif function_name == "update_enrollment":
            data["enrollment_updated"] = True
        elif function_name == "get_enrollment_summary":
            data["enrollment_summary"] = result
            data["ui_hint"] = "enrollment_summary"
        elif function_name == "request_portfolio":
            data["show_portfolio"] = True
            data["ui_hint"] = "portfolio_uploader"
        elif function_name == "submit_enrollment":
            data["enrollment_result"] = result
            data["ui_hint"] = "enrollment_complete"
        
        return data if data else None

    def _parse_ui_elements(self, text: str, data: Optional[Dict]) -> Optional[Dict]:
        """Parse text for UI hints and buttons."""
        if not data:
            data = {}
            
        # 1. Detect Keyword Hints
        lower_text = text.lower()
        if "service catalog" in lower_text or "categories" in lower_text:
            data["ui_hint"] = "service_selector"
        elif "pick a time" in lower_text or "calendar" in lower_text:
            data["ui_hint"] = "calendar_picker"
        elif "location" in lower_text and "?" in lower_text:
             data["ui_hint"] = "location_picker"
             
        # 2. Parse Buttons [button: Text | action]
        import re
        buttons = []
        pattern = r"\[button: (.*?) \| (.*?)\]"
        matches = re.findall(pattern, text)
        for label, action in matches:
            buttons.append({"label": label.strip(), "action": action.strip()})
            
        if buttons:
            data["buttons"] = buttons
            
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
