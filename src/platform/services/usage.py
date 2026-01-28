"""
Proxie LLM Usage Service - Cost Tracking & Guardrails

Calculates costs based on model-specific pricing and enforces
per-user/per-session budget limits.
"""

import structlog
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from src.platform.models.usage import LLMUsage
from src.platform.config import settings

logger = structlog.get_logger(__name__)

class LLMUsageService:
    """Service for tracking LLM costs and enforcing budget limits."""
    
    def __init__(self, db: Session):
        self.db = db

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost in USD based on token counts."""
        # Simple lookup table based on model names
        # Note: In production, this might call LiteLLM's cost calculator directly
        
        input_price = 0.0
        output_price = 0.0
        
        if "gemini-2.0-flash" in model:
            input_price = settings.LLM_GEMINI_2_0_FLASH_INPUT_COST
            output_price = settings.LLM_GEMINI_2_0_FLASH_OUTPUT_COST
        elif "claude-3-5-sonnet" in model:
            input_price = settings.LLM_CLAUDE_3_5_SONNET_INPUT_COST
            output_price = settings.LLM_CLAUDE_3_5_SONNET_OUTPUT_COST
        elif "text-embedding-3-large" in model:
            input_price = settings.LLM_EMBEDDING_3_LARGE_COST
            output_price = 0.0
        
        # Prices are per 1M tokens
        cost = (prompt_tokens * input_price / 1_000_000) + (completion_tokens * output_price / 1_000_000)
        return cost

    def record_usage(
        self, 
        provider: str, 
        model: str, 
        prompt_tokens: int, 
        completion_tokens: int,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        feature: Optional[str] = None
    ) -> LLMUsage:
        """Log LLM usage to the database."""
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        
        usage = LLMUsage(
            user_id=user_id,
            session_id=session_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=cost,
            feature=feature
        )
        
        self.db.add(usage)
        self.db.commit()
        self.db.refresh(usage)
        
        logger.info(
            "llm_usage_recorded", 
            user_id=user_id, 
            cost=f"${cost:.6f}", 
            model=model
        )
        return usage

    def is_over_budget(self, user_id: Optional[str], session_id: Optional[str]) -> bool:
        """Check if user or session has exceeded their budget."""
        if not user_id and not session_id:
            return False # Unauthenticated/untracked allowed for now, or tighten later
            
        # 1. Check Session Limit
        if session_id:
            session_cost = self.db.query(func.sum(LLMUsage.estimated_cost_usd))\
                .filter(LLMUsage.session_id == session_id).scalar() or 0.0
            
            if session_cost >= settings.LLM_SESSION_LIMIT:
                logger.warning("llm_session_budget_exceeded", session_id=session_id, cost=session_cost)
                return True
                
        # 2. Check Daily User Limit
        if user_id:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            daily_cost = self.db.query(func.sum(LLMUsage.estimated_cost_usd))\
                .filter(LLMUsage.user_id == user_id)\
                .filter(LLMUsage.created_at >= today).scalar() or 0.0
                
            if daily_cost >= settings.LLM_DAILY_LIMIT_PER_USER:
                logger.warning("llm_user_daily_budget_exceeded", user_id=user_id, cost=daily_cost)
                return True
                
        return False
