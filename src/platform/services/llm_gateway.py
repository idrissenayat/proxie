"""
Proxie LLM Gateway - LiteLLM Abstraction with Redis Caching

Provides a unified interface for LLM completions with fallback and caching.
"""

import json
import hashlib
import redis
import litellm
import structlog
from typing import List, Dict, Any, Optional
from src.platform.config import settings
from src.platform.metrics import track_llm_usage, LLM_LATENCY_SECONDS
from src.platform.services.usage import LLMUsageService
from src.platform.database import SessionLocal
import time

logger = structlog.get_logger()

class LLMGateway:
    """Gateway for AI model interactions using LiteLLM."""
    
    def __init__(self):
        # Configure LiteLLM
        litellm.set_verbose = settings.DEBUG
        
        # Initialize Redis for caching
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, db=settings.REDIS_CACHE_DB)
            self.cache_enabled = settings.LLM_CACHE_ENABLED
        except Exception as e:
            logger.error("Failed to connect to Redis for LLM caching", error=str(e))
            self.redis_client = None
            self.cache_enabled = False
            
        self.cache_ttl = settings.LLM_CACHE_TTL
        self.primary_model = f"{settings.LLM_PRIMARY_PROVIDER}/{settings.LLM_PRIMARY_MODEL}"
        self.fallback_model = f"{settings.LLM_FALLBACK_PROVIDER}/{settings.LLM_FALLBACK_MODEL}"

    def _get_cache_key(self, model: str, messages: List[Dict], tools: Optional[List] = None) -> str:
        """Generate a deterministic cache key for given inputs."""
        key_data = {
            "model": model,
            "messages": messages,
            "tools": tools
        }
        hash_val = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
        return f"llm_cache:{hash_val}"

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        use_cache: bool = True,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        feature: str = "general"
    ) -> Any:
        """Execute a chat completion with caching and fallback."""
        target_model = model or self.primary_model
        
        # 0. Budget Check
        with SessionLocal() as db:
            usage_service = LLMUsageService(db)
            if usage_service.is_over_budget(user_id, session_id):
                logger.error("LLM Budget Exceeded - Blocking Request", user_id=user_id, session_id=session_id)
                raise Exception("LLM usage limit exceeded for this session/day.")

        # 1. Try Cache
        cache_key = None
        if use_cache and self.cache_enabled and self.redis_client:
            cache_key = self._get_cache_key(target_model, messages, tools)
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    logger.info("LLM Cache Hit", model=target_model)
                    # Use LiteLLM's own response object if possible, or a simple mock
                    try:
                        from litellm.utils import ModelResponse
                        return ModelResponse(**json.loads(cached))
                    except:
                        # Fallback to a simple dot-accessible dict
                        class DotDict(dict):
                            __getattr__ = dict.get
                            __setattr__ = dict.__setitem__
                            __delattr__ = dict.__delitem__
                        
                        def convert(obj):
                            if isinstance(obj, dict):
                                return DotDict({k: convert(v) for k, v in obj.items()})
                            if isinstance(obj, list):
                                return [convert(i) for i in obj]
                            return obj
                        
                        return convert(json.loads(cached))
            except Exception as e:
                logger.error("Redis read error", error=str(e))

        # 1.5 Mock Mode Check
        is_mock = not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY in ["", "your-gemini-api-key", "your-key-here"]
        if is_mock:
            logger.info("LLM Mock Mode Enabled", model=target_model)
            from litellm.utils import ModelResponse
            import json
            
            # Check if we just finished a tool call
            last_msg = messages[-1] if messages else {}
            if last_msg.get("role") == "tool":
                tool_name = last_msg.get("name")
                response_text = "I've processed that for you."
                
                if tool_name == "get_my_leads" or tool_name == "get_matching_requests":
                    response_text = "Here are your current leads."
                elif tool_name == "create_service_request":
                    response_text = "Your request has been created! ✅"
                elif tool_name == "get_service_catalog":
                    response_text = "Please select the services you offer."
                
                # Tool execution complete, return a summary
                mock_response = {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
                }
                import asyncio
                await asyncio.sleep(0.5)
                return ModelResponse(**mock_response)

            content = "I understand you need help. Here is a simulated response from Proxie AI (Mock Mode)."
            tool_calls = []
            
            request_text = str(messages).lower()
            
            # Mock "Create Request" flow
            # Avoid triggering if we already have a tool call or response in history to avoid loops
            # But simpler for now: just strictly check input content
            
            # Mock "Create Request" flow
            # We want to simulate a Draft first, so NO tool call here.
            # We return text that triggers _detect_draft_in_response
            if ("brooklyn" in request_text or "apartment" in request_text) and "create_request" not in request_text:
                content = "I've drafted a cleaning request for your Brooklyn apartment. Here is your request summary. Ready to post?"
                # No tool calls - let the orchestrator/chat service handle draft creation from text/context
                tool_calls = []
            
            # Mock "Service Catalog" flow
            elif "services" in request_text and "name is alex" in request_text:
                content = "Great to meet you, Alex! To get started as a professional cleaner, please select the services you offer from our catalog."
                tool_calls = [{
                    "id": "call_mock_2",
                    "type": "function",
                    "function": {
                        "name": "get_service_catalog",
                        "arguments": "{}"
                    }
                }]
            
            # Mock "Leads" flow
            elif "leads" in request_text and "show me" in request_text:
                content = "Here are your current leads:"
                tool_calls = [{
                    "id": "call_mock_3",
                    "type": "function",
                    "function": {
                        "name": "get_my_leads",
                        "arguments": "{}"
                    }
                }]

            mock_response = {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": tool_calls if tool_calls else None
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 10,
                    "total_tokens": 20
                }
            }
            # Simulate a small delay
            import asyncio
            await asyncio.sleep(0.5)
            return ModelResponse(**mock_response)

        # 2. Attempt Primary Completion
        start_time = time.time()
        try:
            response = await litellm.acompletion(
                model=target_model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Record metrics & DB usage
            latency = time.time() - start_time
            provider = target_model.split('/')[0]
            model_name = target_model.split('/')[-1]
            
            LLM_LATENCY_SECONDS.labels(provider=provider, model=model_name).observe(latency)
            
            if hasattr(response, 'usage') and response.usage:
                # Prometheus
                track_llm_usage(
                    provider=provider,
                    model=model_name,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens
                )
                # Database (Cost Tracking)
                with SessionLocal() as db:
                    LLMUsageService(db).record_usage(
                        provider=provider,
                        model=model_name,
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens,
                        user_id=user_id,
                        session_id=session_id,
                        feature=feature
                    )
            
            # Cache Success
            if use_cache and self.cache_enabled and self.redis_client and cache_key:
                try:
                    self.redis_client.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(response.to_dict())
                    )
                except Exception as e:
                    logger.error("Redis write error", error=str(e))
                    
            return response

        except Exception as e:
            logger.error("LLM Primary Provider Failed", model=target_model, error=str(e))
            
            # Don't fallback if model was explicitly specified and failed
            if model and model != self.primary_model:
                raise e
                
            # Fallback to Secondary
            logger.info("Attempting LLM Fallback", model=self.fallback_model)
            start_time = time.time()
            try:
                response = await litellm.acompletion(
                    model=self.fallback_model,
                    messages=messages,
                    tools=tools,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Record metrics
                latency = time.time() - start_time
                LLM_LATENCY_SECONDS.labels(
                    provider=self.fallback_model.split('/')[0], 
                    model=self.fallback_model.split('/')[-1]
                ).observe(latency)
                
                if hasattr(response, 'usage') and response.usage:
                    # Prometheus
                    track_llm_usage(
                        provider=self.fallback_model.split('/')[0],
                        model=self.fallback_model.split('/')[-1],
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens
                    )
                    # Database
                    with SessionLocal() as db:
                        LLMUsageService(db).record_usage(
                            provider=self.fallback_model.split('/')[0],
                            model=self.fallback_model.split('/')[-1],
                            prompt_tokens=response.usage.prompt_tokens,
                            completion_tokens=response.usage.completion_tokens,
                            user_id=user_id,
                            session_id=session_id,
                            feature=feature
                        )
                    
                return response
            except Exception as e2:
                logger.error("LLM Fallback Failed", model=self.fallback_model, error=str(e2))
                raise e2

# Global instance
llm_gateway = LLMGateway()
