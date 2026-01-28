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
        use_cache: bool = True
    ) -> Any:
        """Execute a chat completion with caching and fallback."""
        target_model = model or self.primary_model
        
        # Try Cache
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

        # Attempt Primary Completion
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
            
            # Record metrics
            latency = time.time() - start_time
            LLM_LATENCY_SECONDS.labels(
                provider=target_model.split('/')[0], 
                model=target_model.split('/')[-1]
            ).observe(latency)
            
            if hasattr(response, 'usage') and response.usage:
                track_llm_usage(
                    provider=target_model.split('/')[0],
                    model=target_model.split('/')[-1],
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens
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
                    track_llm_usage(
                        provider=self.fallback_model.split('/')[0],
                        model=self.fallback_model.split('/')[-1],
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens
                    )
                    
                return response
            except Exception as e2:
                logger.error("LLM Fallback Failed", model=self.fallback_model, error=str(e2))
                raise e2

# Global instance
llm_gateway = LLMGateway()
