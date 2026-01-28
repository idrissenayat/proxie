"""
Proxie Embedding Service - AI Vector Generation

Integrated with LiteLLM to provide high-performance embeddings 
using OpenAI's text-embedding-3-large by default.
"""

import litellm
import structlog
from typing import List, Optional
from src.platform.config import settings
from src.platform.database import SessionLocal
from src.platform.services.usage import LLMUsageService

logger = structlog.get_logger(__name__)

class EmbeddingService:
    """Service for generating vector embeddings from text."""
    
    def __init__(self):
        self.model = settings.LLM_EMBEDDING_MODEL
        # Ensure OpenAI key is set if using OpenAI model
        if "openai" in self.model and not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set, embeddings may fail if using OpenAI model")

    async def get_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a single string."""
        if not text:
            return []
            
        try:
            response = await litellm.aembedding(
                model=self.model,
                input=[text],
                api_key=settings.OPENAI_API_KEY if "openai" in self.model else None
            )
            
            # Record Usage
            if hasattr(response, 'usage') and response.usage:
                with SessionLocal() as db:
                    LLMUsageService(db).record_usage(
                        provider="openai" if "openai" in self.model else "unknown",
                        model=self.model,
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=0,
                        feature="embedding"
                    )
                    
            return response.data[0]["embedding"]
        except Exception as e:
            logger.error("Failed to generate embedding", model=self.model, error=str(e))
            raise e

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of strings in one call."""
        if not texts:
            return []
            
        try:
            response = await litellm.aembedding(
                model=self.model,
                input=texts,
                api_key=settings.OPENAI_API_KEY if "openai" in self.model else None
            )
            
            # Record Usage
            if hasattr(response, 'usage') and response.usage:
                with SessionLocal() as db:
                    LLMUsageService(db).record_usage(
                        provider="openai" if "openai" in self.model else "unknown",
                        model=self.model,
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=0,
                        feature="embedding_batch"
                    )
                    
            return [item["embedding"] for item in response.data]
        except Exception as e:
            logger.error("Failed to generate batch embeddings", model=self.model, error=str(e))
            raise e

# Global instance
embedding_service = EmbeddingService()
