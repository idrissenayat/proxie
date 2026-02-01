"""
Proxie Sessions - Consolidated Entry Point
Redirects to the persistent SessionManager implementation.
"""
from src.platform.services.session_manager import session_manager, SessionManager

__all__ = ["session_manager", "SessionManager"]
