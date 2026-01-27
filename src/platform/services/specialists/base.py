"""
Base Specialist Agent for Proxie.

Defines the interface and base class for all specialist agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SpecialistAnalysis:
    """Result of a specialist's analysis."""
    is_valid: bool
    enriched_data: Dict[str, Any]  # Professional terminology and structured data
    missing_info: List[str]  # Things the specialist needs but doesn't have
    suggestions: List[str]  # Helpful suggestions for the user
    hair_type: Optional[str] = None  # For haircut specialist
    service_complexity: Optional[str] = None  # low, medium, high
    estimated_duration: Optional[str] = None  # e.g., "1-2 hours"
    notes: Optional[str] = None  # Internal notes (not shown to user)


class SpecialistAgent(ABC):
    """
    Base class for specialist agents.
    
    Specialist agents are domain experts that can:
    - Analyze media (photos/videos) for domain-specific details
    - Validate that a request has all necessary information
    - Enrich requests with professional terminology
    - Suggest additional information needed
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The specialist's name (e.g., 'Haircut Specialist')."""
        pass
    
    @property
    @abstractmethod
    def service_categories(self) -> List[str]:
        """Service categories this specialist handles."""
        pass
    
    @abstractmethod
    async def analyze(
        self,
        service_type: str,
        description: str,
        location: Dict[str, str],
        budget: Dict[str, float],
        timing: Optional[str],
        media_descriptions: List[str],
        additional_context: Dict[str, Any]
    ) -> SpecialistAnalysis:
        """
        Analyze a service request and provide enriched data.
        
        Args:
            service_type: The type of service requested
            description: User's description of what they need
            location: Location information
            budget: Budget range (min, max)
            timing: Timing preference
            media_descriptions: Descriptions of any attached media (from vision AI)
            additional_context: Any other context gathered during conversation
            
        Returns:
            SpecialistAnalysis with enriched data and suggestions
        """
        pass
    
    def can_handle(self, service_category: str) -> bool:
        """Check if this specialist can handle a given service category."""
        return service_category.lower() in [c.lower() for c in self.service_categories]


class SpecialistRegistry:
    """Registry for specialist agents."""
    
    def __init__(self):
        self._specialists: Dict[str, SpecialistAgent] = {}
    
    def register(self, category: str, specialist: SpecialistAgent):
        """Register a specialist for a service category."""
        self._specialists[category.lower()] = specialist
        logger.info(f"Registered specialist: {specialist.name} for category: {category}")
    
    def get(self, category: str) -> Optional[SpecialistAgent]:
        """Get a specialist for a service category."""
        return self._specialists.get(category.lower())
    
    def find_for_service(self, service_type: str) -> Optional[SpecialistAgent]:
        """Find a specialist that can handle a service type."""
        # Direct match
        service_lower = service_type.lower()
        if service_lower in self._specialists:
            return self._specialists[service_lower]
        
        # Check if any specialist can handle it
        for specialist in self._specialists.values():
            if specialist.can_handle(service_type):
                return specialist
        
        # Check for keywords
        keywords = {
            "haircut": ["hair", "cut", "style", "trim", "color", "dye", "highlights", "balayage"],
            "cleaning": ["clean", "maid", "housekeeping", "tidy"],
            "plumbing": ["plumb", "pipe", "leak", "drain", "faucet", "toilet"],
        }
        
        for category, terms in keywords.items():
            if any(term in service_lower for term in terms):
                if category in self._specialists:
                    return self._specialists[category]
        
        return None
    
    def list_all(self) -> List[str]:
        """List all registered specialist categories."""
        return list(self._specialists.keys())
