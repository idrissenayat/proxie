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
from src.platform.services.memory_service import MemoryService
from src.platform.services.handoff_manager import HandoffManager
from src.platform.services.session_manager import session_manager

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from src.platform.services.orchestrator import proxie_orchestrator

logger = structlog.get_logger(__name__)

from src.platform.services.prompts import (
    CONSUMER_SYSTEM_PROMPT, 
    PROVIDER_SYSTEM_PROMPT, 
    ENROLLMENT_SYSTEM_PROMPT,
    EXTRACTION_PROMPT
)
from src.platform.services.context_tracker import ConversationContext, ContextSource

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
        "name": "recall_preferences",
        "description": "Recall specific user preferences from long-term memory. Use this when the user asks 'What is my budget?' or 'Do you remember my style?'.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Specific preference key to look up (e.g., 'budget', 'hair_style', 'location')"}
            }
        }
    },
    {
        "name": "update_preferences",
        "description": "Explicitly update a user's long-term preferences. Use this when the user says 'My new budget is $100' or 'I moved to Queens'. For budgets, if a single value is provided, use it for both budget_min and budget_max.",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_min": {"type": "number"},
                "budget_max": {"type": "number"},
                "location": {"type": "string"},
                "timing": {"type": "string"},
                "communication_style": {"type": "string"}
            }
        }
    },
    {
        "name": "draft_offer",
        "description": "Draft an offer to a consumer.",
        "parameters": {
            "type": "object",
            "properties": {
                "price": {"type": "number", "description": "Offer price"},
                "message": {"type": "string", "description": "Personal message to consumer"}
            },
            "required": ["price", "message"]
        }
    },
    {
        "name": "request_quotes_from_agents",
        "description": "Ask provider agents for quotes on a request.",
        "parameters": {
            "type": "object",
            "properties": {
                "provider_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of provider UUIDs to query"
                },
                "request_details": {
                    "type": "object",
                    "description": "Override details of the request (optional)"
                }
            },
            "required": ["provider_ids"]
        }
    },
    {
        "name": "get_booking_history",
        "description": "Get a list of the user's past bookings. Useful for 'Rebook my last haircut' or 'When was my cleaning?'.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "suggest_providers",
        "description": "Find providers similar to ones the user has liked before. Use this when the user asks for recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "service_category": {"type": "string"}
            }
        }
    },
    {
        "name": "update_request_details",
        "description": "Update the current service request draft with details provided by the user (service type, location, budget, etc.). Call this as soon as you extract these details from the conversation to ensure they are remembered. If a single budget value is provided, use it for both budget_min and budget_max.",
        "parameters": {
            "type": "object",
            "properties": {
                "service_type": {"type": "string", "description": "Type of service needed (e.g., 'haircut', 'cleaning')"},
                "description": {"type": "string", "description": "Detailed description of the request"},
                "city": {"type": "string", "description": "City where service is needed"},
                "budget_min": {"type": "number", "description": "Minimum budget in dollars"},
                "budget_max": {"type": "number", "description": "Maximum budget in dollars"},
                "timing": {"type": "string", "description": "When the service is needed"}
            }
        }
    },
    {
        "name": "create_service_request",
        "description": "Create a service request AFTER user has approved the draft. This posts the request to find providers. For budget, use provided values or sensible ranges.",
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

    async def extract_information(self, message: str) -> dict:
        """
        Extract all structured information from user message.
        Called BEFORE main agent response.
        """
        from src.platform.services.llm_gateway import llm_gateway
        
        try:
            extraction_response = await llm_gateway.chat_completion(
                messages=[{
                    "role": "user",
                    "content": EXTRACTION_PROMPT.format(message=message)
                }],
                # Using JSON mode helper if available, otherwise just parse text
                max_tokens=500,
                temperature=0,
                use_cache=True # Enable cache for extraction too
            )
            
            content = extraction_response.choices[0].message.content
            # Clean up potential markdown formatting
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                 content = content.split("```")[1].split("```")[0].strip()
            
            extracted = json.loads(content)
            # Filter out null values
            return {k: v for k, v in extracted.items() if v is not None}
        except Exception as e:
            logger.error(f"Failed to extract information (skipping): {e}")
            # If extraction fails, we still want to proceed with the main chat
            # The agent will have to rely on the general history
            return {}


    def _is_mock_mode(self) -> bool:
        return not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY in ["", "your-gemini-api-key", "your-key-here"]

    def _to_lc_msgs(self, messages: List[Dict]) -> List[BaseMessage]:
        """Convert Proxie/Gemini dict messages to LangChain messages."""
        lc_msgs = []
        for m in messages:
            role = m.get("role")
            content = m.get("content")
            if role == "user":
                lc_msgs.append(HumanMessage(content=content))
            elif role == "assistant":
                # Handle tool calls
                kwargs = {}
                if "tool_calls" in m:
                    kwargs["tool_calls"] = m["tool_calls"]
                lc_msgs.append(AIMessage(content=content or "", additional_kwargs=kwargs))
            elif role == "tool":
                lc_msgs.append(ToolMessage(
                    tool_call_id=m.get("tool_call_id"),
                    name=m.get("name"),
                    content=str(m.get("content"))
                ))
            elif role == "system":
                lc_msgs.append(SystemMessage(content=content))
        return lc_msgs

    def _from_lc_msgs(self, lc_msgs: List[BaseMessage]) -> List[Dict]:
        """Convert LangChain messages back to Proxie/Gemini dicts."""
        messages = []
        for m in lc_msgs:
            if isinstance(m, HumanMessage):
                messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                msg_dict = {"role": "assistant", "content": m.content}
                if "tool_calls" in m.additional_kwargs:
                    msg_dict["tool_calls"] = m.additional_kwargs["tool_calls"]
                messages.append(msg_dict)
            elif isinstance(m, ToolMessage):
                messages.append({
                    "role": "tool",
                    "tool_call_id": m.tool_call_id,
                    "name": m.name,
                    "content": m.content
                })
            elif isinstance(m, SystemMessage):
                messages.append({"role": "system", "content": m.content})
        return messages

    def _get_model_params(self, role: str, provider_id: Optional[UUID] = None) -> Tuple[str, List[Dict]]:
        """Get specialized model parameters based on role."""
        # Note: Prompts are now dynamic and injected in handle_chat
        prompt = CONSUMER_SYSTEM_PROMPT # Fallback
        tools = self._get_openai_tools(TOOL_DECLARATIONS)
        
        if role == "provider":
            prompt = PROVIDER_SYSTEM_PROMPT
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
        media: List[MediaAttachment] = None,
        action: Optional[str] = None,
        clerk_id: Optional[str] = None
    ) -> Tuple[str, str, Optional[Dict], Optional[DraftRequest], bool]:
        """
        Main entry point for handling a chat message.
        """
        # Load or create session
        session_id, session = self._get_or_create_session(session_id, role, provider_id) # Keep original order for now
        
        # Check for role transition (Handoff)
        is_handoff, handoff_msg = HandoffManager.check_handoff(
            session, 
            role, 
            user_name=session["context"].get("consumer_profile", {}).get("name", "User")
        )
        
        if is_handoff and handoff_msg:
            # Inject system notice so the agent knows to welcome the user
            # We add it as a system message at the end of history, or a user message from "System"
            session["messages"].append({
                "role": "system", 
                "content": f"[SYSTEM EVENT]: {handoff_msg} (The user has upgraded/changed roles. Greet them accordingly.)"
            })
        
        # Hydrate context
        session["context"]["session_id"] = session_id
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
                if not consumer and consumer_id:
                    # Check if the guest record can be "claimed"
                    guest_consumer = db.query(Consumer).filter(Consumer.id == UUID(str(consumer_id))).first()
                    if guest_consumer and not guest_consumer.clerk_id:
                        guest_consumer.clerk_id = clerk_id
                        db.commit()
                        db.refresh(guest_consumer)
                        consumer = guest_consumer
                        logger.info("guest_profile_claimed", clerk_id=clerk_id, consumer_id=consumer_id)
                
                if consumer:
                    session["context"]["consumer_profile"] = consumer.to_dict()
                else:
                    # Create a default profile if not exists
                    consumer = Consumer(clerk_id=clerk_id)
                    db.add(consumer)
                    db.commit()
                    db.refresh(consumer)
                    session["context"]["consumer_profile"] = consumer.to_dict()
                
                # Update consumer_id context to match the claimed/found record's UUID
                session["context"]["consumer_id"] = str(consumer.id)
                consumer_id = str(consumer.id) # Sync local var
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
        
        # 2. Initialize context tracker
        context_obj = ConversationContext(**session["context"])
        
        # Diagnostic: Log session state
        messages = session.get("messages", [])
        logger.info(
            "chat_context_check",
            session_id=session_id,
            message_count=len(messages),
            has_history=len(messages) > 0,
            known_facts=context_obj.get_known_summary()
        )
        
        # 3. Load profile into context if available
        if "consumer_profile" in session["context"]:
            context_obj.update_from_profile(session["context"]["consumer_profile"])
        
        # 4. Extract information from CURRENT message BEFORE responding
        if message:
            extracted = await self.extract_information(message)
            if extracted:
                context_obj.update_from_extraction(extracted, ContextSource.CURRENT_MESSAGE)
                # Update legacy gathered_info for backward compatibility with some tools
                session["context"]["gathered_info"] = {**session["context"].get("gathered_info", {}), **extracted}
        
        # Sync context_obj back to session dict
        session["context"].update(context_obj.dict())

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
        
        # LOGIC CHANGE: We now use llm_gateway mock mode within the orchestrator.
        # So we disable this legacy bypass.
        # if self.is_mock:
        #     response_text, data = self._mock_response(message, role, session["context"], stored_media)
        #     return session_id, response_text, data, session["context"].get("draft"), session["context"].get("awaiting_approval", False)
        
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
            
            # System Prompt is handled by orchestrator, skip inserting into history here
            # to avoid redundancy and conflicting context.
            
            # Add to session messages
            session["messages"].append({"role": "user", "content": content_list})
            
            # Prepare Context for Orchestrator
            session["context"]["tools"] = session["tools"]
            session["context"]["tool_executor"] = lambda name, args: self._execute_tool(name, args, session["context"])
            
            # Convert existing history to LangChain
            lc_messages = self._to_lc_msgs(session["messages"])
            
            # Run Orchestrator (LangGraph)
            response_text, final_lc_msgs, final_context = await proxie_orchestrator.run(
                messages=lc_messages,
                context=session["context"],
                user_id=clerk_id or consumer_id or provider_id,
                session_id=session_id,
                role=role
            )
            
            # Sync back context and history
            session["context"] = final_context
            session["messages"] = self._from_lc_msgs(final_lc_msgs)
            
            # Auto-save relevant info to profile
            if role == "consumer" and (clerk_id or consumer_id):
                 # re-instantiate context to use update logic if needed, but for now just direct save
                 await self._auto_save_consumer_profile(session["context"], clerk_id or consumer_id)
            
            # Structured data and UI hints (legacy support)
            # Find any tool results in history to pull structured data
            structured_data = None
            for m in reversed(session["messages"]):
                if m["role"] == "tool":
                    structured_data = self._capture_structured_data(m["name"], json.loads(m["content"]), structured_data)
            
            # Consult Specialist if relevant (SpecialistAgent logic)
            await self._consult_specialist(session["context"], message, response_text, stored_media)
            
            # Check if response indicates a draft
            draft = self._detect_draft_in_response(response_text, session["context"])
            awaiting_approval = draft is not None
            
            if draft:
                session["context"]["draft"] = draft.dict() if hasattr(draft, 'dict') else draft
                session["context"]["awaiting_approval"] = True
            
            # Parse UI hints and buttons from final response
            structured_data = self._parse_ui_elements(response_text, structured_data)
            
            # Cleanup non-serializable items
            if "tool_executor" in session["context"]:
                del session["context"]["tool_executor"]

            # Save session
            session_manager.save_session(session_id, session)
            
            return session_id, response_text, structured_data, draft, awaiting_approval
            
        except Exception as e:
            logger.exception("Error in handle_chat")
            # Re-raise so controller can handle with proper status codes
            # or include error info in message for tests/UI
            error_msg = str(e)
            if "limit exceeded" in error_msg.lower():
                return session_id, "LLM usage limit exceeded for this session/day.", None, None, False
            return session_id, f"Error: {error_msg}", None, None, False

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
            
            # Helper to access draft attributes safely whether it's an object or dict
            def get_attr(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            # Create the actual service request
            try:
                # Handle media - might be list of objects or list of dicts
                draft_media = get_attr(draft, "media", [])
                media_list = []
                for m in draft_media:
                    if isinstance(m, dict):
                        media_list.append(m)
                    elif hasattr(m, 'dict'):
                        media_list.append(m.dict())
                
                # Access timing and location safely
                draft_timing = get_attr(draft, "timing")
                draft_location = get_attr(draft, "location", {})
                draft_budget = get_attr(draft, "budget", {})

                result = await self._execute_tool(
                    "create_service_request",
                    {
                        "service_type": get_attr(draft, "service_type"),
                        "description": get_attr(draft, "description"),
                        "city": draft_location.get("city", "") if isinstance(draft_location, dict) else getattr(draft_location, "city", ""),
                        "budget_min": draft_budget.get("min", 0) if isinstance(draft_budget, dict) else getattr(draft_budget, "min", 0),
                        "budget_max": draft_budget.get("max", 100) if isinstance(draft_budget, dict) else getattr(draft_budget, "max", 100),
                        "timing": draft_timing or "",
                        "media": media_list,
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
                
                # Normalize location to dict if it's a string
                location = info.get("location")
                if isinstance(location, str):
                    location = {"city": location}
                elif not location:
                    location = {"city": info.get("city") or "Unknown"}
                
                # Normalize budget
                budget = info.get("budget")
                if not budget:
                    budget = {
                        "min": info.get("budget_min") or 0,
                        "max": info.get("budget_max") or 100
                    }

                return DraftRequest(
                    service_type=info.get("service_type") or info.get("service_subtype") or "Service",
                    service_category="hair" if "hair" in lower else "general",
                    description=info.get("description", ""),
                    details={k: v for k, v in info.items() if k not in ["service_type", "service_subtype", "description", "location", "budget", "timing", "budget_min", "budget_max", "city", "address"]},
                    location=location,
                    budget=budget,
                    timing=info.get("timing"),
                    media=media,
                    specialist_notes=analysis.notes if hasattr(analysis, 'notes') else (analysis.get('notes') if isinstance(analysis, dict) else None)
                )
        return None

    async def _execute_tool(self, name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool/function and return results."""
        try:
            cid = context.get("consumer_id")
            consumer_uuid = UUID(cid) if cid else None

            if name == "recall_preferences":
                if not consumer_uuid:
                    return {"error": "No user identity found"}
                from src.platform.database import SessionLocal
                with SessionLocal() as db:
                    mem_service = MemoryService(db)
                    ctx = await mem_service.get_consumer_context(consumer_uuid)
                    memory = ctx.get("memory")
                    
                    # Check explicit
                    exp_key = f"preferred_{params.get('key')}"
                    if hasattr(memory, exp_key) and getattr(memory, exp_key):
                        return {"preference": getattr(memory, exp_key), "source": "explicit"}
                    
                    # Check learned
                    learned = getattr(memory, "learned_preferences", {}) or {}
                    if params.get('key') in learned:
                         return {"preference": learned[params.get('key')], "source": "learned"}
                         
                    return {"message": "No specific preference found for this."}
                
            elif name == "update_preferences":
                if not consumer_uuid:
                    return {"error": "No user identity found"}
                
                # Just call update_consumer_memory with a special interaction type
                interaction = {
                    "session_id": context.get("session_id"),
                    "type": "explicit_preference_update",
                    "input": "User updated preferences via tool",
                    "output": "Preferences updated",
                    "tools": [{"name": "update_preferences", "args": params}],
                    "outcome": "success"
                }
                
                from src.platform.database import SessionLocal
                with SessionLocal() as db:
                    mem_service = MemoryService(db)
                    await mem_service.update_consumer_memory(consumer_uuid, interaction)
                return {"status": "success", "message": "Preferences updated"}
            
            elif name == "get_booking_history":
                if not consumer_uuid:
                    return {"error": "No user identity found"}
                
                from src.platform.database import SessionLocal
                with SessionLocal() as db:
                    mem_service = MemoryService(db)
                    ctx = await mem_service.get_consumer_context(consumer_uuid)
                    bookings = ctx.get("recent_bookings", [])
                    
                return {
                    "bookings": [
                        {
                            "id": str(b.id),
                            "service": b.service_id, 
                            "date": b.created_at.strftime('%Y-%m-%d'),
                            "status": b.status
                        } for b in bookings
                    ]
                }
            
            elif name == "suggest_providers":
                 # Mock implementation for now until search service is upgraded
                 return {"suggestions": ["Provider A (High Rating)", "Provider B (Good Price)"]}

            elif name == "create_service_request":
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
                
                result = await handlers.create_service_request(
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
                
            elif name == "update_request_details":
                gathered = context.get("gathered_info", {})
                for key, value in params.items():
                    if value:
                        if key == "city":
                            gathered["location"] = gathered.get("location", {})
                            if isinstance(gathered["location"], dict):
                                gathered["location"]["city"] = value
                        elif key in ["budget_min", "budget_max"]:
                            gathered["budget"] = gathered.get("budget", {})
                            if isinstance(gathered["budget"], dict):
                                b_key = "min" if key == "budget_min" else "max"
                                gathered["budget"][b_key] = value
                        else:
                            gathered[key] = value
                
                context["gathered_info"] = gathered
                
                # Create a human-readable summary of what was updated
                updates = [k for k, v in params.items() if v]
                msg = f"Successfully updated request details: {', '.join(updates)}. "
                if 'city' in updates: msg += f"Location set to {params['city']}. "
                msg += "Context is saved. DO NOT ask the user for these details again."
                
                return {"status": "success", "message": msg, "gathered_info": gathered}
                
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
            
            elif name == "get_my_leads":
                # Mock leads
                return {
                    "leads": [
                        {
                            "id": str(uuid.uuid4()),
                            "service_type": "Haircut",
                            "description": "Fade and trim",
                            "budget": 60,
                            "location": "Downtown",
                            "created_at": "2026-01-28 10:00:00",
                            "match_score": 0.9
                        }
                    ]
                }
                
            elif name == "suggest_offer":
                provider_id = params.get("provider_id") or context.get("provider_id")
                if not provider_id:
                     return {"error": "Provider ID required"}
                     
                # Get pricing history
                history_price = 80 # Default
                try:
                    ctx = await self.memory_service.get_provider_context(UUID(provider_id))
                    # Basic logic: avg of last 5 offers
                    recent = ctx.get("recent_offers", [])
                    if recent:
                        prices = [float(o.price) for o in recent if o.price]
                        if prices:
                            history_price = sum(prices) / len(prices)
                except Exception as e:
                    logger.warning("Failed to get pricing history", error=str(e))
                
                return {
                    "suggestion": {
                        "price": history_price,
                        "rationale": f"Based on your history (avg ${history_price}) and market rates.",
                        "message": "I'd love to help you with this!"
                    }
                }
                
            elif name == "draft_offer":
                return {
                    "draft": {
                        "id": str(uuid.uuid4()),
                        "status": "draft",
                        "price": params.get("price"),
                        "message": params.get("message")
                    },
                    "message": "Draft created! Review above."
                }
                
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
            
            

            
            elif name == "request_quotes_from_agents":
                from src.platform.services.a2a_protocol import a2a_protocol
                
                # Extract params
                provider_ids = params.get("provider_ids", [])
                request_details = params.get("request_details", context.get("gathered_info", {}))
                
                # Call Protocol
                # Note: In production, this would be async/background. For MVP, we await.
                try:
                    quotes = await a2a_protocol.request_quotes(request_details, provider_ids)
                    return {
                        "status": "success",
                        "count": len(quotes),
                        "quotes": quotes,
                        "summary": f"Received {len(quotes)} quotes from providers."
                    }
                except Exception as e:
                    logger.error("Failed to request quotes", error=str(e))
                    return {"error": "Failed to negotiate with agents."}

            else:
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
        elif function_name == "update_request_details":
            data["gathered_info"] = result.get("gathered_info")
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


    async def _auto_save_consumer_profile(self, context_dict: Dict, consumer_id_or_clerk: str):
        """Automatically save relevant extracted info to user profile."""
        from src.platform.database import SessionLocal
        from src.platform.models.consumer import Consumer
        from uuid import UUID
        
        try:
            with SessionLocal() as db:
                # Try to find by UUID first (internal id)
                try:
                    target_id = UUID(consumer_id_or_clerk)
                    consumer = db.query(Consumer).filter(Consumer.id == target_id).first()
                except (ValueError, TypeError):
                    # Fallback to clerk_id
                    consumer = db.query(Consumer).filter(Consumer.clerk_id == consumer_id_or_clerk).first()
                
                if consumer:
                    # Update name if missing
                    if context_dict.get("name") and not consumer.name:
                        consumer.name = context_dict["name"]
                    
                    # Update location if missing
                    if context_dict.get("city") and not consumer.default_location:
                        consumer.default_location = {"city": context_dict["city"]}
                    
                    # Merge preferences
                    if context_dict.get("preferences"):
                        existing = consumer.preferences or {}
                        consumer.preferences = {**existing, **context_dict["preferences"]}
                    
                    db.commit()
                    logger.info("consumer_profile_autosaved", consumer_id=str(consumer.id))
        except Exception as e:
            logger.error(f"Failed to auto-save consumer profile: {e}")

# Global service instance
chat_service = ChatService()
