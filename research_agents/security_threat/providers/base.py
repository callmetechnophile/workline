"""
Abstract base reasoning provider for SecurityThreatModelingAgent (Agent #22).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    ThreatMitigation,
    ThreatObject,
)


class ReasoningProvider(ABC):
    """Abstract interface for LLM-assisted threat scenario analysis and mitigation drafting."""

    @abstractmethod
    async def analyze_threat_scenarios(
        self,
        project_context: Dict[str, Any],
        assets: List[AssetObject],
        attack_surface: List[AttackSurfaceEntry],
    ) -> List[ThreatObject]:
        """Draft threat scenarios based on discovered assets and entry points."""
        pass

    @abstractmethod
    async def suggest_security_mitigations(
        self,
        threat: ThreatObject,
        attack_path: AttackPath,
    ) -> List[ThreatMitigation]:
        """Propose actionable security mitigations and controls."""
        pass
