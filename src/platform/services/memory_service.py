"""
Proxie Memory Service.

Handles persistent context memory for consumer and provider agents.
"""

import structlog
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from src.platform.models.memory import ConsumerMemory, ProviderMemory, AgentInteraction, SpecialistKnowledge
from src.platform.models.booking import Booking
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.services.embeddings import embedding_service
from src.platform.database import SessionLocal

logger = structlog.get_logger(__name__)

class MemoryService:
    """Service for managing agent memory and context."""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def get_consumer_context(self, consumer_id: UUID) -> Dict[str, Any]:
        """Retrieve full context for a Personal Consumer Agent."""
        
        # 1. Get persistent memory
        stmt = select(ConsumerMemory).where(ConsumerMemory.consumer_id == consumer_id)
        result = self.db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            # Initialize empty memory if none exists
            memory = ConsumerMemory(consumer_id=consumer_id)
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            
        # 2. Get recent activity
        bookings = self.db.query(Booking).filter(
            Booking.consumer_id == consumer_id
        ).order_by(Booking.created_at.desc()).limit(5).all()
        
        requests = self.db.query(ServiceRequest).filter(
            ServiceRequest.consumer_id == consumer_id
        ).order_by(ServiceRequest.created_at.desc()).limit(5).all()
        
        # 3. Construct context object
        return {
            "memory": memory,
            "recent_bookings": bookings,
            "recent_requests": requests,
            "summary": self._generate_consumer_summary(memory, bookings)
        }
        
    async def update_consumer_memory(self, consumer_id: UUID, interaction_data: Dict[str, Any]):
        """Update consumer memory based on an interaction."""
        
        # Log interaction first
        interaction = AgentInteraction(
            session_id=interaction_data.get("session_id"),
            agent_type="personal_consumer",
            user_id=consumer_id,
            interaction_type=interaction_data.get("type"),
            input_summary=interaction_data.get("input"),
            output_summary=interaction_data.get("output"),
            tools_used=interaction_data.get("tools", []),
            outcome=interaction_data.get("outcome")
        )
        self.db.add(interaction)
        
        # Get memory
        stmt = select(ConsumerMemory).where(ConsumerMemory.consumer_id == consumer_id)
        memory = self.db.execute(stmt).scalar_one_or_none()
        
        if not memory:
            memory = ConsumerMemory(consumer_id=consumer_id)
            self.db.add(memory)
            
        # Update observable stats
        if interaction.outcome == "booking_confirmed":
            memory.total_bookings += 1
        
        if interaction.tools_used:
            await self._infer_preferences(memory, interaction)
            
        self.db.commit()
        
    async def _infer_preferences(self, memory: ConsumerMemory, interaction: AgentInteraction):
        """Analyze interaction to update learned preferences."""
        # Simple heuristic for now: if user provided specific preferences in tool calls, save them
        for tool in interaction.tools_used:
            if tool["name"] == "update_preferences":
                args = tool.get("args", {})
                current_prefs = dict(memory.learned_preferences) if memory.learned_preferences else {}
                
                # Update Explicit Preferences
                if "budget_min" in args:
                    memory.preferred_budget_min = args["budget_min"]
                if "budget_max" in args:
                    memory.preferred_budget_max = args["budget_max"]
                if "timing" in args:
                    memory.preferred_timing = args["timing"]
                if "communication_style" in args:
                    memory.communication_style = args["communication_style"]
                
                # Update Learned Preferences for location (since it's JSON)
                if "location" in args:
                    current_prefs["last_location"] = args["location"]
                
                memory.learned_preferences = current_prefs
                
                # Trigger Embedding Update
                pref_text = f"Budget: {memory.preferred_budget_min}-{memory.preferred_budget_max}, Location: {current_prefs.get('last_location')}, Timing: {memory.preferred_timing}"
                try:
                    memory.preference_embedding = await embedding_service.get_embedding(pref_text)
                except Exception as e:
                    logger.warning("Failed to generate preference embedding", error=str(e))

            elif tool["name"] == "update_request_details":
                args = tool.get("args", {})
                
                # Update learned preferences JSON
                current_prefs = dict(memory.learned_preferences) if memory.learned_preferences else {}
                
                if "budget" in args:
                    current_prefs["last_budget_hint"] = args["budget"]
                if "location" in args:
                    current_prefs["last_location"] = args["location"]
                    
                memory.learned_preferences = current_prefs
                
                # If explicit preferences provided, update columns
                if "budget_min" in args:
                    memory.preferred_budget_min = args["budget_min"]
                if "budget_max" in args:
                    memory.preferred_budget_max = args["budget_max"]

                # Re-compute embedding if significant info added
                # For v1, we just embed the summary of preferences
                pref_text = f"Budget: {memory.preferred_budget_min}-{memory.preferred_budget_max}, Location: {current_prefs.get('last_location')}"
                try:
                    memory.preference_embedding = await embedding_service.get_embedding(pref_text)
                except Exception as e:
                    logger.warning("Failed to generate preference embedding", error=str(e))
                    # Continue without embedding - graceful degradation

    def _generate_consumer_summary(self, memory: ConsumerMemory, bookings: List[Booking]) -> str:
        """Generate a natural language summary for the agent system prompt."""
        summary_parts = []
        
        if memory.preferred_budget_min and memory.preferred_budget_max:
            summary_parts.append(f"Budget preference: ${memory.preferred_budget_min}-${memory.preferred_budget_max}")
            
        if memory.learned_preferences:
            loc = memory.learned_preferences.get("last_location")
            if loc:
                summary_parts.append(f"Usually requests services in {loc}")
                
        if bookings:
            last_booking = bookings[0]
            summary_parts.append(f"Last booking was for {last_booking.service_id} on {last_booking.created_at.strftime('%Y-%m-%d')}")
            
        return ". ".join(summary_parts) if summary_parts else "New user with no history."

    async def get_provider_context(self, provider_id: UUID) -> Dict[str, Any]:
        """Retrieve full context for a Personal Provider Agent."""
        stmt = select(ProviderMemory).where(ProviderMemory.provider_id == provider_id)
        memory = self.db.execute(stmt).scalar_one_or_none()
        
        if not memory:
            memory = ProviderMemory(provider_id=provider_id)
            self.db.add(memory)
            self.db.commit()
            
        # Get recent offers
        offers = self.db.query(Offer).filter(
            Offer.provider_id == provider_id
        ).order_by(Offer.created_at.desc()).limit(10).all()
        
        return {
            "memory": memory,
            "recent_offers": offers,
            "performance": {
                "leads": memory.total_leads_received,
                "offers": memory.total_offers_sent,
                "conversion": float(memory.conversion_rate or 0)
            }
        }
