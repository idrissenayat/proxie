"""
Haircut Specialist Agent for Proxie.

Analyzes hair-related service requests, identifies hair types from photos,
and enriches requests with professional terminology.
"""

from typing import Dict, Any, List, Optional
import logging

from src.platform.services.specialists.base import SpecialistAgent, SpecialistAnalysis

logger = logging.getLogger(__name__)


# Hair type classification (Andre Walker System)
HAIR_TYPES = {
    "1A": "Type 1A - Fine straight hair",
    "1B": "Type 1B - Medium straight hair", 
    "1C": "Type 1C - Coarse straight hair",
    "2A": "Type 2A - Loose S-waves",
    "2B": "Type 2B - Defined S-waves",
    "2C": "Type 2C - Strong waves",
    "3A": "Type 3A - Loose curls (big loops)",
    "3B": "Type 3B - Springy curls (ringlets)",
    "3C": "Type 3C - Tight curls (corkscrews)",
    "4A": "Type 4A - Soft coils (S-pattern)",
    "4B": "Type 4B - Z-pattern coils",
    "4C": "Type 4C - Tight Z-pattern coils",
}

# Haircut styles knowledge base
HAIRCUT_STYLES = {
    "bob": ["classic bob", "a-line bob", "inverted bob", "lob (long bob)", "asymmetric bob"],
    "pixie": ["classic pixie", "long pixie", "undercut pixie", "textured pixie"],
    "layers": ["long layers", "short layers", "face-framing layers", "choppy layers"],
    "bangs": ["curtain bangs", "side-swept bangs", "blunt bangs", "wispy bangs", "baby bangs"],
    "fade": ["low fade", "mid fade", "high fade", "skin fade", "drop fade"],
    "undercut": ["disconnected undercut", "undercut with design"],
    "shag": ["modern shag", "70s shag", "wolf cut"],
    "other": ["trim", "shape up", "taper", "mullet", "buzz cut"],
}

# Color services
COLOR_SERVICES = {
    "highlights": ["foil highlights", "balayage", "babylights", "partial highlights", "full highlights"],
    "lowlights": ["lowlights"],
    "full_color": ["single process", "all-over color", "root touch-up"],
    "creative": ["ombre", "sombre", "color melt", "fantasy color", "vivid color"],
    "corrective": ["color correction", "toner", "gloss"],
}

# Treatments
TREATMENTS = {
    "keratin": ["keratin treatment", "Brazilian blowout", "smoothing treatment"],
    "conditioning": ["deep conditioning", "hair mask", "hot oil treatment"],
    "repair": ["bond repair", "Olaplex treatment", "K18 treatment"],
    "scalp": ["scalp treatment", "scalp detox"],
}


class HaircutSpecialist(SpecialistAgent):
    """
    Specialist agent for haircut and hair care services.
    
    Capabilities:
    - Identify hair type from descriptions (and photos via Gemini)
    - Understand haircut terminology
    - Enrich vague descriptions with professional terms
    - Flag missing information
    - Suggest helpful photos if needed
    """
    
    @property
    def name(self) -> str:
        return "Haircut Specialist"
    
    @property
    def service_categories(self) -> List[str]:
        return [
            "haircut", "hair", "hairstyle", "hair color", "highlights", 
            "balayage", "trim", "cut", "styling", "blowout", "keratin",
            "hair treatment", "color correction"
        ]
    
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
        Analyze a hair service request.
        """
        enriched_data = {}
        missing_info = []
        suggestions = []
        notes_parts = []
        
        # Combine all text for analysis
        full_text = f"{service_type} {description} " + " ".join(media_descriptions)
        full_text_lower = full_text.lower()
        
        # Detect service sub-type
        service_subtype = self._detect_service_type(full_text_lower)
        enriched_data["service_subtype"] = service_subtype
        notes_parts.append(f"Service type: {service_subtype}")
        
        # Detect hair type from media descriptions
        hair_type = self._detect_hair_type(media_descriptions, full_text_lower)
        if hair_type:
            enriched_data["hair_type"] = hair_type
            enriched_data["hair_type_description"] = HAIR_TYPES.get(hair_type, hair_type)
            notes_parts.append(f"Detected hair type: {hair_type}")
        
        # Detect style preferences
        styles = self._detect_styles(full_text_lower)
        if styles:
            enriched_data["requested_styles"] = styles
            notes_parts.append(f"Requested styles: {', '.join(styles)}")
        
        # Detect color services
        color_services = self._detect_color_services(full_text_lower)
        if color_services:
            enriched_data["color_services"] = color_services
            notes_parts.append(f"Color services: {', '.join(color_services)}")
        
        # Detect treatments
        treatments = self._detect_treatments(full_text_lower)
        if treatments:
            enriched_data["treatments"] = treatments
            notes_parts.append(f"Treatments: {', '.join(treatments)}")
        
        # Estimate complexity
        complexity = self._estimate_complexity(service_subtype, color_services, treatments)
        enriched_data["complexity"] = complexity
        
        # Estimate duration
        duration = self._estimate_duration(service_subtype, color_services, treatments)
        enriched_data["estimated_duration"] = duration
        
        # Check for missing information
        if not media_descriptions:
            missing_info.append("No photos provided")
            suggestions.append("A photo of your current hair would help stylists understand your needs better")
        elif len(media_descriptions) == 1 and "back" not in full_text_lower:
            suggestions.append("A photo of the back of your hair can help show current length and layers")
        
        if not hair_type and not media_descriptions:
            missing_info.append("Hair type unknown")
        
        if service_subtype == "unknown":
            missing_info.append("Specific service not clear")
            suggestions.append("What type of service are you looking for - a cut, color, or treatment?")
        
        # Check budget appropriateness
        budget_feedback = self._check_budget(budget, service_subtype, color_services, treatments)
        if budget_feedback:
            suggestions.append(budget_feedback)
        
        # Determine validity
        is_valid = len(missing_info) == 0 or (
            "No photos provided" in missing_info and len(missing_info) == 1
        )
        
        return SpecialistAnalysis(
            is_valid=is_valid,
            enriched_data=enriched_data,
            missing_info=missing_info,
            suggestions=suggestions,
            hair_type=hair_type,
            service_complexity=complexity,
            estimated_duration=duration,
            notes="; ".join(notes_parts) if notes_parts else None
        )
    
    def _detect_service_type(self, text: str) -> str:
        """Detect the primary service type."""
        if any(word in text for word in ["color", "dye", "highlight", "balayage", "ombre"]):
            if any(word in text for word in ["cut", "trim", "style"]):
                return "cut_and_color"
            return "color"
        if any(word in text for word in ["keratin", "treatment", "conditioning", "repair"]):
            return "treatment"
        if any(word in text for word in ["blowout", "blow dry", "styling"]):
            return "styling"
        if any(word in text for word in ["cut", "trim", "haircut", "bob", "pixie", "layers", "fade"]):
            return "haircut"
        return "unknown"
    
    def _detect_hair_type(self, media_descriptions: List[str], text: str) -> Optional[str]:
        """Detect hair type from media descriptions or text."""
        combined = " ".join(media_descriptions).lower() + " " + text
        
        # Check for explicit mentions
        for code, desc in HAIR_TYPES.items():
            if code.lower() in combined or desc.lower() in combined:
                return code
        
        # Check for descriptive keywords
        if "coily" in combined or "coils" in combined:
            if "tight" in combined or "4c" in combined:
                return "4C"
            if "z-pattern" in combined or "4b" in combined:
                return "4B"
            return "4A"
        
        if "curly" in combined or "curls" in combined:
            if "tight" in combined or "corkscrew" in combined:
                return "3C"
            if "springy" in combined or "ringlet" in combined:
                return "3B"
            if "loose" in combined or "big" in combined:
                return "3A"
            return "3B"  # Default curly
        
        if "wavy" in combined or "waves" in combined:
            if "strong" in combined or "defined" in combined:
                return "2C"
            if "s-wave" in combined or "s wave" in combined:
                return "2B"
            return "2A"
        
        if "straight" in combined:
            if "fine" in combined or "thin" in combined:
                return "1A"
            if "coarse" in combined or "thick" in combined:
                return "1C"
            return "1B"
        
        return None
    
    def _detect_styles(self, text: str) -> List[str]:
        """Detect requested haircut styles."""
        found = []
        for category, styles in HAIRCUT_STYLES.items():
            if category in text:
                found.append(category)
            for style in styles:
                if style in text:
                    found.append(style)
        return list(set(found))
    
    def _detect_color_services(self, text: str) -> List[str]:
        """Detect color services."""
        found = []
        for category, services in COLOR_SERVICES.items():
            for service in services:
                if service in text:
                    found.append(service)
        return list(set(found))
    
    def _detect_treatments(self, text: str) -> List[str]:
        """Detect treatments."""
        found = []
        for category, treatments in TREATMENTS.items():
            for treatment in treatments:
                if treatment in text:
                    found.append(treatment)
        return list(set(found))
    
    def _estimate_complexity(
        self, 
        service_type: str, 
        color_services: List[str], 
        treatments: List[str]
    ) -> str:
        """Estimate service complexity."""
        if service_type == "cut_and_color" or len(color_services) > 1:
            return "high"
        if color_services or treatments:
            return "medium"
        if service_type in ["color", "treatment"]:
            return "medium"
        return "low"
    
    def _estimate_duration(
        self, 
        service_type: str, 
        color_services: List[str], 
        treatments: List[str]
    ) -> str:
        """Estimate service duration."""
        if service_type == "cut_and_color":
            return "2-4 hours"
        if "color correction" in color_services:
            return "3-6 hours"
        if any("full" in c or "all-over" in c for c in color_services):
            return "2-3 hours"
        if color_services:
            return "1.5-2.5 hours"
        if treatments:
            return "1-2 hours"
        if service_type == "styling":
            return "30-60 minutes"
        # Basic haircut
        return "30-60 minutes"
    
    def _check_budget(
        self, 
        budget: Dict[str, float], 
        service_type: str, 
        color_services: List[str], 
        treatments: List[str]
    ) -> Optional[str]:
        """Check if budget seems appropriate for the service."""
        min_budget = budget.get("min", 0)
        max_budget = budget.get("max", 0)
        
        if max_budget == 0:
            return None
        
        # Rough price estimates (varies by location, but gives a sense)
        if service_type == "cut_and_color" and max_budget < 150:
            return f"Your budget of ${max_budget} might be tight for cut and color. Many salons charge $150-300+ for this service."
        
        if color_services and max_budget < 100:
            return f"Color services typically start around $100-150. Your budget of ${max_budget} might limit options."
        
        if any("keratin" in t for t in treatments) and max_budget < 200:
            return "Keratin treatments typically cost $200-400+. You may want to adjust your budget."
        
        return None
