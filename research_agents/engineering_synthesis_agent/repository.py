"""
Repository interface for EngineeringSynthesisAgent decisions, trade-offs, risks, and validation plans.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.engineering_synthesis_agent.schemas import (
    DecisionTraceability,
    EngineeringDecision,
    EngineeringRisk,
    EngineeringSynthesisAgentOutput,
    EngineeringTradeoff,
    RecommendationItem,
    RequirementAnalysis,
    TechnicalFinding,
    ValidationRequirement,
)


class EngineeringDecisionRepository(ABC):
    """Abstract persistence interface for engineering synthesis decisions and validation records."""

    @abstractmethod
    async def save_requirement_analysis(self, req: RequirementAnalysis, project_id: str) -> str:
        """Persists requirement coverage mapping."""
        pass

    @abstractmethod
    async def save_finding(self, finding: TechnicalFinding, project_id: str) -> str:
        """Persists technical finding."""
        pass

    @abstractmethod
    async def save_tradeoff(self, tradeoff: EngineeringTradeoff, project_id: str) -> str:
        """Persists trade-off analysis."""
        pass

    @abstractmethod
    async def save_decision(self, decision: EngineeringDecision, project_id: str) -> str:
        """Persists engineering design decision."""
        pass

    @abstractmethod
    async def save_recommendation(self, rec: RecommendationItem, project_id: str) -> str:
        """Persists engineering recommendation."""
        pass

    @abstractmethod
    async def save_risk(self, risk: EngineeringRisk, project_id: str) -> str:
        """Persists engineering risk."""
        pass

    @abstractmethod
    async def save_validation_requirement(self, val: ValidationRequirement, project_id: str) -> str:
        """Persists validation requirement."""
        pass

    @abstractmethod
    async def save_traceability(self, trace: DecisionTraceability, project_id: str) -> str:
        """Persists requirement -> decision -> validation traceability."""
        pass

    @abstractmethod
    async def save_output(self, output: EngineeringSynthesisAgentOutput) -> str:
        """Persists full synthesis output."""
        pass

    @abstractmethod
    async def get_output(self, project_id: str) -> Optional[EngineeringSynthesisAgentOutput]:
        """Retrieves synthesis output by project ID."""
        pass


class InMemoryEngineeringDecisionRepository(EngineeringDecisionRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._outputs: Dict[str, EngineeringSynthesisAgentOutput] = {}
        self._decisions: Dict[str, List[EngineeringDecision]] = {}
        self._tradeoffs: Dict[str, List[EngineeringTradeoff]] = {}
        self._risks: Dict[str, List[EngineeringRisk]] = {}
        self._validations: Dict[str, List[ValidationRequirement]] = {}

    async def save_requirement_analysis(self, req: RequirementAnalysis, project_id: str) -> str:
        return f"{project_id}_{req.requirement_id}"

    async def save_finding(self, finding: TechnicalFinding, project_id: str) -> str:
        return f"{project_id}_{finding.finding_id}"

    async def save_tradeoff(self, tradeoff: EngineeringTradeoff, project_id: str) -> str:
        if project_id not in self._tradeoffs:
            self._tradeoffs[project_id] = []
        self._tradeoffs[project_id].append(tradeoff)
        return f"{project_id}_{tradeoff.tradeoff_id}"

    async def save_decision(self, decision: EngineeringDecision, project_id: str) -> str:
        if project_id not in self._decisions:
            self._decisions[project_id] = []
        self._decisions[project_id].append(decision)
        return f"{project_id}_{decision.decision_id}"

    async def save_recommendation(self, rec: RecommendationItem, project_id: str) -> str:
        return f"{project_id}_{rec.recommendation_id}"

    async def save_risk(self, risk: EngineeringRisk, project_id: str) -> str:
        if project_id not in self._risks:
            self._risks[project_id] = []
        self._risks[project_id].append(risk)
        return f"{project_id}_{risk.risk_id}"

    async def save_validation_requirement(self, val: ValidationRequirement, project_id: str) -> str:
        if project_id not in self._validations:
            self._validations[project_id] = []
        self._validations[project_id].append(val)
        return f"{project_id}_{val.validation_id}"

    async def save_traceability(self, trace: DecisionTraceability, project_id: str) -> str:
        return f"{project_id}_trace_{trace.decision_id}"

    async def save_output(self, output: EngineeringSynthesisAgentOutput) -> str:
        proj_id = output.project.project_id or output.project.title
        self._outputs[proj_id] = output
        return proj_id

    async def get_output(self, project_id: str) -> Optional[EngineeringSynthesisAgentOutput]:
        return self._outputs.get(project_id)
