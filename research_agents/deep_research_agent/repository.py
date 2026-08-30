"""
Repository interface for DeepResearchAgent synthesis reports and claims.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.deep_research_agent.schemas import (
    ComponentTradeStudy,
    DeepResearchAgentOutput,
    EngineeringRecommendation,
    SynthesizedClaim,
)


class SynthesisRepository(ABC):
    """Abstract persistence interface for synthesis reports, claims, trade studies, and recommendations."""

    @abstractmethod
    async def save_report(self, output: DeepResearchAgentOutput) -> str:
        """Persists full deep research report."""
        pass

    @abstractmethod
    async def save_claim(self, claim: SynthesizedClaim, project_id: str) -> str:
        """Persists a single synthesized claim."""
        pass

    @abstractmethod
    async def save_trade_study(self, study: ComponentTradeStudy, project_id: str) -> str:
        """Persists a component trade study."""
        pass

    @abstractmethod
    async def save_recommendation(self, rec: EngineeringRecommendation, project_id: str) -> str:
        """Persists an engineering recommendation."""
        pass

    @abstractmethod
    async def get_report(self, project_id: str) -> Optional[DeepResearchAgentOutput]:
        """Retrieves research report by project ID."""
        pass

    @abstractmethod
    async def get_project_claims(self, project_id: str) -> List[SynthesizedClaim]:
        """Retrieves all claims associated with a project."""
        pass


class InMemorySynthesisRepository(SynthesisRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._reports: Dict[str, DeepResearchAgentOutput] = {}
        self._claims: Dict[str, List[SynthesizedClaim]] = {}
        self._trade_studies: Dict[str, List[ComponentTradeStudy]] = {}
        self._recommendations: Dict[str, List[EngineeringRecommendation]] = {}

    async def save_report(self, output: DeepResearchAgentOutput) -> str:
        proj_id = output.project.project_id or output.project.title
        self._reports[proj_id] = output
        self._claims[proj_id] = output.extracted_claims
        self._trade_studies[proj_id] = output.component_trade_studies
        self._recommendations[proj_id] = output.recommendations
        return proj_id

    async def save_claim(self, claim: SynthesizedClaim, project_id: str) -> str:
        if project_id not in self._claims:
            self._claims[project_id] = []
        self._claims[project_id].append(claim)
        return f"{project_id}_claim_{len(self._claims[project_id])}"

    async def save_trade_study(self, study: ComponentTradeStudy, project_id: str) -> str:
        if project_id not in self._trade_studies:
            self._trade_studies[project_id] = []
        self._trade_studies[project_id].append(study)
        return f"{project_id}_trade_{len(self._trade_studies[project_id])}"

    async def save_recommendation(self, rec: EngineeringRecommendation, project_id: str) -> str:
        if project_id not in self._recommendations:
            self._recommendations[project_id] = []
        self._recommendations[project_id].append(rec)
        return f"{project_id}_rec_{len(self._recommendations[project_id])}"

    async def get_report(self, project_id: str) -> Optional[DeepResearchAgentOutput]:
        return self._reports.get(project_id)

    async def get_project_claims(self, project_id: str) -> List[SynthesizedClaim]:
        return self._claims.get(project_id, [])
