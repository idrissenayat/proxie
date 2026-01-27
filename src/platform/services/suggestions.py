from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

class SuggestionResponse(BaseModel):
    suggested_price: Dict[str, float]  # low, recommended, high
    reasoning: str
    suggested_duration: int
    available_slots: List[Dict[str, str]]
    suggested_message: str

class OfferSuggestionService:
    """Provides AI-driven pricing and timing suggestions for providers."""

    async def suggest_offer(
        self, 
        request_data: Dict[str, Any], 
        provider_data: Dict[str, Any]
    ) -> SuggestionResponse:
        """
        Analyze a lead and provider profile to recommend the best offer structure.
        """
        # Extract metadata
        analysis = request_data.get("specialist_analysis", {})
        budget = request_data.get("budget", {})
        budget_min = budget.get("min", 0)
        budget_max = budget.get("max", 100)
        
        # Determine complexity
        complexity = analysis.get("complexity", "standard").lower()
        est_duration = analysis.get("estimated_duration_minutes", 60)
        
        # Provider base rates
        # Find relevant service base price
        service_type = request_data.get("service_type")
        provider_base_price = 0
        for s in provider_data.get("services", []):
            if s.get("type") == service_type:
                provider_base_price = s.get("base_price", 0)
                break
        
        if not provider_base_price:
            provider_base_price = provider_data.get("base_price", 50)

        # Calculation logic (Heuristic based for MVP)
        # Recommended is usually the midpoint of consumer budget if it aligns with provider base
        if complexity == "complex":
            multiplier = 1.25
        elif complexity == "simple":
            multiplier = 0.85
        else:
            multiplier = 1.0
            
        adjusted_provider_price = provider_base_price * multiplier
        
        # Clamp to consumer budget if possible, but stay closer to provider worth
        recommended = max(budget_min, min(budget_max, adjusted_provider_price))
        
        low = max(budget_min, recommended * 0.9)
        high = min(budget_max, recommended * 1.2)
        
        # Reasoning
        reasoning = f"Based on {complexity} complexity and your base rate of ${provider_base_price}. "
        reasoning += f"Consumer budget is ${budget_min}-${budget_max}."

        # Template for message
        suggested_message = f"Hi! I see you're looking for a {service_type}. "
        if analysis.get("hair_type"):
            suggested_message += f"I specialize in {analysis.get('hair_type')} hair and would love to help. "
        suggested_message += "I have availability during your preferred time."

        return SuggestionResponse(
            suggested_price={"low": low, "recommended": recommended, "high": high},
            reasoning=reasoning,
            suggested_duration=est_duration,
            available_slots=self._get_mock_slots(),
            suggested_message=suggested_message
        )

    def _get_mock_slots(self) -> List[Dict[str, str]]:
        # In a real app, this would check the provider's actual calendar
        return [
            {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "time": "14:00"},
            {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "time": "15:30"},
            {"date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), "time": "10:00"}
        ]

suggestion_service = OfferSuggestionService()
