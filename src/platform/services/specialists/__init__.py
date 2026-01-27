"""
Specialist Agents for Proxie.

This module provides domain-specific specialist agents that can be consulted
by the Consumer Agent to validate and enrich service requests.
"""

from src.platform.services.specialists.base import SpecialistAgent, SpecialistRegistry
from src.platform.services.specialists.haircut import HaircutSpecialist

# Register all specialists
specialist_registry = SpecialistRegistry()
specialist_registry.register("haircut", HaircutSpecialist())
specialist_registry.register("hair", HaircutSpecialist())  # Alias

__all__ = [
    "SpecialistAgent",
    "SpecialistRegistry", 
    "specialist_registry",
    "HaircutSpecialist",
]
