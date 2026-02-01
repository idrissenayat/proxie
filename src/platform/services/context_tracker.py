"""
Context Tracker: Accumulates and tracks all known information about the user
to prevent redundant questions.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timezone

class ContextSource(str, Enum):
    PROFILE = "profile"           # From stored user profile
    CURRENT_MESSAGE = "current"   # Extracted from current user message
    CONVERSATION = "conversation" # From earlier in this conversation
    MEDIA_ANALYSIS = "media"      # From specialist image/video analysis


class KnownFact(BaseModel):
    """A single piece of known information"""
    key: str
    value: Any
    source: ContextSource
    confidence: float = 1.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ConversationContext(BaseModel):
    """Tracks all known information for a conversation session"""
    
    # Core user info
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    default_location: Optional[str] = None
    
    # Service request info
    service_type: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    timing: Optional[str] = None  # asap, this_week, specific_date
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    
    # Preferences (from conversation or media analysis)
    preferences: Dict[str, Any] = {}
    
    # Provider-specific (for enrollment)
    business_name: Optional[str] = None
    years_experience: Optional[int] = None
    services_offered: List[str] = []
    service_radius_km: Optional[int] = None
    portfolio_photos: List[str] = []
    bio: Optional[str] = None
    
    # Tracking
    facts_log: List[KnownFact] = []
    
    def update_from_profile(self, profile: dict) -> None:
        """Load known facts from user profile"""
        mappings = {
            'name': 'name',
            'email': 'email', 
            'phone': 'phone',
            'default_location': 'default_location',
            'preferences': 'preferences'
        }
        for profile_key, context_key in mappings.items():
            if profile.get(profile_key):
                # Special handling for preferences to merge
                if context_key == 'preferences':
                    existing = getattr(self, 'preferences', {})
                    merged = {**existing, **profile[profile_key]}
                    setattr(self, 'preferences', merged)
                else:
                    setattr(self, context_key, profile[profile_key])
                
                self.facts_log.append(KnownFact(
                    key=context_key,
                    value=profile[profile_key],
                    source=ContextSource.PROFILE
                ))
            
            # Sync default_location to requirement field 'location'
            if profile.get('default_location') and not self.location:
                self.location = profile['default_location']
    
    def update_from_extraction(self, extracted: dict, source: ContextSource) -> None:
        """Update context from AI extraction"""
        for key, value in extracted.items():
            if value is not None and hasattr(self, key):
                current = getattr(self, key)
                # Only update if not already known (or if from more specific source)
                # For now, let's say 'current' is more specific than 'conversation'
                if current is None or current == [] or current == {}:
                    setattr(self, key, value)
                    self.facts_log.append(KnownFact(
                        key=key,
                        value=value,
                        source=source
                    ))
                elif source == ContextSource.CURRENT_MESSAGE:
                    # Update if it's from the current message (user correction)
                    setattr(self, key, value)
                    self.facts_log.append(KnownFact(
                        key=key,
                        value=value,
                        source=source
                    ))
            
            # Cross-sync geographical info
            if key == "city" and not self.location:
                self.location = value
            elif key == "location" and not self.city:
                # If location looks like just a city (no numbers), sync it
                if value and not any(c.isdigit() for c in str(value)):
                    self.city = value
    
    def get_known_summary(self) -> Dict[str, Any]:
        """Return dict of all known (non-None) values"""
        data = self.dict()
        # Synthetic field for requirements check: if we have city or address, we have location
        if (data.get('city') or data.get('address')) and not data.get('location'):
            data['location'] = data.get('city') or data.get('address')
            
        return {k: v for k, v in data.items() 
                if v is not None and v != [] and v != {} and k != 'facts_log'}
    
    def get_missing_required(self, intent: str) -> List[str]:
        """Return list of required fields still missing for given intent"""
        requirements = INTENT_REQUIREMENTS.get(intent, [])
        known = self.get_known_summary()
        return [field for field in requirements if field not in known]
    
    def get_missing_optional(self, intent: str) -> List[str]:
        """Return list of optional fields that could improve the request"""
        optional = INTENT_OPTIONAL.get(intent, [])
        known = self.get_known_summary()
        return [field for field in optional if field not in known]


# Define what's required vs optional for each intent
INTENT_REQUIREMENTS = {
    "service_request": ["service_type", "location"],
    "booking": ["service_type", "location", "timing", "provider_id"],
    "enrollment": ["name", "services_offered", "location"],
    "offer": ["request_id", "price", "available_date", "available_time"],
}

INTENT_OPTIONAL = {
    "service_request": ["budget_min", "budget_max", "timing", "preferences", "preferred_date"],
    "booking": ["budget_max", "preferences"],
    "enrollment": ["business_name", "bio", "years_experience", "portfolio_photos", "service_radius_km"],
}
