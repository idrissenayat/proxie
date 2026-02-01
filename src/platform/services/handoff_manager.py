from typing import Dict, Any, Optional, Tuple

class HandoffManager:
    """Manages transitions between agent roles with context preservation."""
    
    @staticmethod
    def check_handoff(
        session: Dict[str, Any], 
        new_role: str, 
        user_name: Optional[str] = "User"
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines if a handoff is required based on role change.
        Returns (is_handoff, transition_message).
        """
        current_role = session.get("context", {}).get("role")
        
        # 1. Guest -> Personal Consumer
        if current_role == "guest" and new_role == "consumer":
            return True, f"Welcome back, {user_name}! I've connected to your personal history. I see you were looking for services - let's find the perfect match for you."
            
        # 2. Enrollment -> Personal Provider
        elif current_role == "enrollment" and new_role == "provider":
            return True, f"Congratulations, {user_name}! Your profile is active. I'm now your dedicated Business Manager. Let's look at your first leads."

        # 3. No change or invalid transition
        if current_role == new_role:
             return False, None
             
        # Catch-all for other role switches (e.g. consumer <-> provider logic if we supported it)
        if current_role and current_role != new_role:
             return True, f"Switching to {new_role} mode."
             
        return False, None
