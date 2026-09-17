"""
Abstract base reasoning provider for EngineeringRiskAgent (Agent #21).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from research_agents.engineering_risk.schemas import FailureMode, RiskMitigation, RiskObject


class ReasoningProvider(ABC):
    """Abstract interface for LLM-assisted failure mode extraction and mitigation suggestions."""

    @abstractmethod
    async def extract_failure_modes(
        self,
        project_context: Dict[str, Any],
        architecture: Dict[str, Any],
        bom: Dict[str, Any],
        interfaces: List[Dict[str, Any]],
    ) -> List[FailureMode]:
        """Extract plausible failure modes from engineering descriptions."""
        pass

    @abstractmethod
    async def suggest_mitigations(
        self,
        risk: RiskObject,
        failure_mode: FailureMode,
    ) -> List[RiskMitigation]:
        """Propose technical mitigations (preventive, detective, corrective, compensating)."""
        pass
