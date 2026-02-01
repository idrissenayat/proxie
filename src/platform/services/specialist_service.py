import yaml
import os
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)

class SpecialistService:
    """Manages domain specialists."""
    
    def __init__(self, knowledge_dir: str = "src/platform/knowledge"):
        self.knowledge_dir = knowledge_dir
        self.specialists: Dict[str, Dict[str, Any]] = {}
        self._load_specialists()
        
    def _load_specialists(self):
        """Load all YAML files from knowledge dir."""
        if not os.path.exists(self.knowledge_dir):
            logger.warning(f"Knowledge dir {self.knowledge_dir} not found")
            return
            
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                name = filename.split(".")[0]
                try:
                    with open(os.path.join(self.knowledge_dir, filename), "r") as f:
                        data = yaml.safe_load(f)
                        self.specialists[name] = data
                    logger.info("Loaded specialist", name=name)
                except Exception as e:
                    logger.error("Failed to load specialist", name=name, error=str(e))
                    
    def get_specialist(self, name: str) -> Optional[Dict[str, Any]]:
        return self.specialists.get(name)
        
    def consult(self, specialist_name: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Consult a specialist. 
        For MVP, this performs keyword matching against the knowledge base.
        In future, this would be an LLM call with the knowledge base as RAG context.
        """
        knowledge = self.get_specialist(specialist_name)
        if not knowledge:
            return {"error": f"Specialist {specialist_name} not found"}
            
        # Basic logical analysis (rules engine)
        
        # 1. Check for technical terms
        terms_found = []
        for term in knowledge.get("technical_terms", []):
            if term.lower() in query.lower():
                terms_found.append(term)
                
        # 2. Check for warnings
        warnings = []
        for key, warning in knowledge.get("warnings", {}).items():
            # Heuristic: match key (e.g. "color_correction") loosely in query
            if key.replace("_", " ") in query.lower():
                warnings.append(warning)
                
        # 3. Estimate Price Multiplier
        multiplier = 1.0
        factors_found = []
        
        pricing = knowledge.get("pricing_factors", {})
        
        # Check service type
        for stype, factor in pricing.get("service_type", {}).items():
            if stype.replace("_", " ") in query.lower():
                multiplier *= factor
                factors_found.append(f"Service: {stype} (x{factor})")
                
        # Check length (mock context check)
        if context and "hair_length" in context:
            length = context["hair_length"]
            if length in pricing.get("hair_length", {}):
                factor = pricing["hair_length"][length]
                multiplier *= factor
                factors_found.append(f"Length: {length} (x{factor})")

        return {
            "specialist": specialist_name,
            "terms_identified": terms_found,
            "warnings": warnings,
            "complexity_multiplier": round(multiplier, 2),
            "pricing_factors": factors_found,
            "analysis": f"identified {len(terms_found)} technical terms. Complexity factor: {round(multiplier, 2)}x."
        }

specialist_service = SpecialistService()
