"""
Abstract base reasoning provider for Manufacturing / DFM-DFA Agent (Agent #24).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from research_agents.manufacturing_agent.schemas import (
    DFAFinding,
    DFMFinding,
    ManufacturingProcess,
    ManufacturingRecommendation,
)


class ReasoningProvider(ABC):
    """Abstract reasoning provider for DFM/DFA engineering interpretation and recommendation drafting."""

    @abstractmethod
    async def analyze_dfm_dfa(
        self,
        project_context: Dict[str, Any],
        components: List[Dict[str, Any]],
        assemblies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Extract DFM/DFA findings from engineering drawings/BOM/specifications."""
        pass

    @abstractmethod
    async def draft_recommendations(
        self,
        dfm_findings: List[DFMFinding],
        dfa_findings: List[DFAFinding],
    ) -> List[ManufacturingRecommendation]:
        """Propose design changes to improve manufacturability and assembly efficiency."""
        pass
