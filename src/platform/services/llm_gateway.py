"""
Proxie LLM Gateway - LiteLLM Abstraction with Redis Caching

Provides a unified interface for LLM completions with fallback and caching.
"""

import json
import hashlib
import redis
import litellm
from litellm.utils import ModelResponse
import structlog
from typing import List, Dict, Any, Optional
from src.platform.config import settings
from src.platform.metrics import (
    track_llm_usage,
    track_llm_request,
    track_llm_cost,
    track_cache_hit,
    track_cache_miss,
    track_cache_error,
    track_cache_set,
    LLM_LATENCY_SECONDS,
    CACHE_LATENCY_SECONDS,
)
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

    def _normalize_messages(self, messages: List[Dict]) -> List[Dict]:
        """Normalize messages for consistent cache key generation."""
        normalized = []
        for msg in messages:
            # Remove timestamp fields, keep only content
            normalized_msg = {
                "role": msg.get("role"),
                "content": msg.get("content"),
            }
            # Include tool_calls if present
            if "tool_calls" in msg:
                normalized_msg["tool_calls"] = msg["tool_calls"]
            normalized.append(normalized_msg)
        return normalized
    
    def _get_cache_key(
        self,
        model: str,
        messages: List[Dict],
        tools: Optional[List] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Generate a deterministic cache key for given inputs."""
        # Normalize messages for consistent hashing
        normalized_messages = self._normalize_messages(messages)
        
        key_data = {
            "model": model,
            "messages": normalized_messages,
            "tools": tools,
            "user_id": user_id  # Include user_id for personalization
        }
        def uuid_convert(obj):
            if isinstance(obj, UUID):
                return str(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        # Use SHA256 for better distribution
        from uuid import UUID
        hash_val = hashlib.sha256(json.dumps(key_data, sort_keys=True, default=uuid_convert).encode()).hexdigest()
        return f"llm_cache:{hash_val}"
    
    def invalidate_cache(self, pattern: Optional[str] = None) -> int:
        """
        Invalidate LLM cache entries.
        
        Args:
            pattern: Optional pattern to match (e.g., "llm_cache:*user_123*")
                    If None, invalidates all LLM cache entries.
        
        Returns:
            Number of keys deleted
        """
        if not self.cache_enabled or not self.redis_client:
            return 0
        
        try:
            pattern = pattern or "llm_cache:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("Cache invalidation error", pattern=pattern, error=str(e))
            return 0
    
    def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache entries for a specific user."""
        # Note: This requires scanning all keys, which is inefficient
        # For better performance, consider using Redis sets to track user cache keys
        return self.invalidate_cache(f"llm_cache:*{user_id}*")
    
    def invalidate_session_cache(self, session_id: str) -> int:
        """Invalidate all cache entries for a specific session."""
        return self.invalidate_cache(f"llm_cache:*session_{session_id}*")

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
            cache_key = self._get_cache_key(target_model, messages, tools, user_id)
            cache_start = time.time()
            try:
                cached = self.redis_client.get(cache_key)
                cache_latency = time.time() - cache_start
                CACHE_LATENCY_SECONDS.labels(cache_type="llm", operation="get").observe(cache_latency)

                if cached:
                    logger.info("LLM Cache Hit", model=target_model)
                    track_cache_hit("llm")
                    # Use LiteLLM's own response object if possible, or a simple mock
                    try:
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
                else:
                    track_cache_miss("llm")
            except Exception as e:
                logger.error("Redis read error", error=str(e))
                track_cache_error("llm", "get")

        # 1.5 Mock Mode Check
        is_mock = settings.ENVIRONMENT in ["test", "testing"] or not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY in ["", "your-gemini-api-key", "your-key-here"]
        if is_mock:
            logger.info("LLM Mock Mode Enabled", model=target_model)
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
            
            # Track successful request
            track_llm_request(provider, model_name, "success")
            track_llm_cost(provider, model_name, response.usage.prompt_tokens, response.usage.completion_tokens)

            # Cache Success
            if use_cache and self.cache_enabled and self.redis_client and cache_key:
                cache_start = time.time()
                try:
                    self.redis_client.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(response.to_dict())
                    )
                    CACHE_LATENCY_SECONDS.labels(cache_type="llm", operation="set").observe(time.time() - cache_start)
                    track_cache_set("llm")
                except Exception as e:
                    logger.error("Redis write error", error=str(e))
                    track_cache_error("llm", "set")
                    
            return response

        except Exception as e:
            logger.error("LLM Primary Provider Failed", model=target_model, error=str(e))
            track_llm_request(target_model.split('/')[0], target_model.split('/')[-1], "error")

            # Don't fallback if model was explicitly specified and failed
            if model and model != self.primary_model:
                raise e

            # Fallback to Secondary
            logger.info("Attempting LLM Fallback", model=self.fallback_model)
            track_llm_request(target_model.split('/')[0], target_model.split('/')[-1], "fallback")
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
