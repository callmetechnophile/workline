"""
Repository interface for EngineeringValidationAgent verification records, rules, and verdicts.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback (Section 45).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.engineering_validation_agent.schemas import (
    EngineeringValidationAgentOutput,
    FinalVerdict,
    RequirementValidationItem,
    ValidationItem,
    ValidationTraceabilityItem,
)


class ValidationRepository(ABC):
    """Abstract persistence interface for engineering design verification records."""

    @abstractmethod
    async def save_validation(self, output: EngineeringValidationAgentOutput) -> str:
        """Persists full validation model output."""
        pass

    @abstractmethod
    async def save_validation_rule_result(self, item: ValidationItem, project_id: str) -> str:
        """Persists single rule evaluation result."""
        pass

    @abstractmethod
    async def save_requirement_status(self, req: RequirementValidationItem, project_id: str) -> str:
        """Persists requirement verification status."""
        pass

    @abstractmethod
    async def save_design_verdict(self, verdict: FinalVerdict, project_id: str) -> str:
        """Persists design quality gate verdict."""
        pass

    @abstractmethod
    async def save_validation_traceability(self, tr: ValidationTraceabilityItem, project_id: str) -> str:
        """Persists validation traceability record."""
        pass

    @abstractmethod
    async def get_validation(self, project_id: str) -> Optional[EngineeringValidationAgentOutput]:
        """Retrieves validation report by project ID."""
        pass


class InMemoryValidationRepository(ValidationRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._validations: Dict[str, EngineeringValidationAgentOutput] = {}
        self._rule_results: Dict[str, List[ValidationItem]] = {}
        self._requirement_results: Dict[str, List[RequirementValidationItem]] = {}
        self._verdicts: Dict[str, FinalVerdict] = {}
        self._traceability: Dict[str, List[ValidationTraceabilityItem]] = {}

    async def save_validation(self, output: EngineeringValidationAgentOutput) -> str:
        proj_id = output.project_id or output.validation_id
        self._validations[proj_id] = output
        return proj_id

    async def save_validation_rule_result(self, item: ValidationItem, project_id: str) -> str:
        if project_id not in self._rule_results:
            self._rule_results[project_id] = []
        self._rule_results[project_id].append(item)
        return f"{project_id}_{item.validation_id}"

    async def save_requirement_status(self, req: RequirementValidationItem, project_id: str) -> str:
        if project_id not in self._requirement_results:
            self._requirement_results[project_id] = []
        self._requirement_results[project_id].append(req)
        return f"{project_id}_{req.requirement_id}"

    async def save_design_verdict(self, verdict: FinalVerdict, project_id: str) -> str:
        self._verdicts[project_id] = verdict
        return f"{project_id}_verdict"

    async def save_validation_traceability(self, tr: ValidationTraceabilityItem, project_id: str) -> str:
        if project_id not in self._traceability:
            self._traceability[project_id] = []
        self._traceability[project_id].append(tr)
        return f"{project_id}_{tr.traceability_id}"

    async def get_validation(self, project_id: str) -> Optional[EngineeringValidationAgentOutput]:
        return self._validations.get(project_id)
