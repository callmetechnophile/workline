"""
Repository interface for ComponentPlanningAgent BOM items, component requirements, and validation requirements.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback (Section 41).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.component_planning_agent.schemas import (
    BOMItem,
    BOMValidationItem,
    ComponentAlternativeItem,
    ComponentPlanningAgentOutput,
    ComponentRequirementItem,
)


class BOMRepository(ABC):
    """Abstract persistence interface for Bill of Materials (BOM) datasets."""

    @abstractmethod
    async def save_bom(self, output: ComponentPlanningAgentOutput) -> str:
        """Persists full BOM dataset."""
        pass

    @abstractmethod
    async def save_bom_item(self, item: BOMItem, project_id: str) -> str:
        """Persists single BOM line item."""
        pass

    @abstractmethod
    async def save_component_requirement(self, req: ComponentRequirementItem, project_id: str) -> str:
        """Persists technical component requirement."""
        pass

    @abstractmethod
    async def save_component_alternative(self, alt: ComponentAlternativeItem, project_id: str) -> str:
        """Persists component alternative evaluation."""
        pass

    @abstractmethod
    async def save_bom_validation(self, val: BOMValidationItem, project_id: str) -> str:
        """Persists BOM validation requirement."""
        pass

    @abstractmethod
    async def save_bom_relationship(self, source_id: str, target_id: str, rel_type: str) -> str:
        """Persists graph relationship."""
        pass

    @abstractmethod
    async def get_bom(self, project_id: str) -> Optional[ComponentPlanningAgentOutput]:
        """Retrieves BOM dataset by project ID."""
        pass


class InMemoryBOMRepository(BOMRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._boms: Dict[str, ComponentPlanningAgentOutput] = {}
        self._items: Dict[str, List[BOMItem]] = {}
        self._requirements: Dict[str, List[ComponentRequirementItem]] = {}
        self._alternatives: Dict[str, List[ComponentAlternativeItem]] = {}
        self._validations: Dict[str, List[BOMValidationItem]] = {}
        self._relationships: List[Dict[str, str]] = []

    async def save_bom(self, output: ComponentPlanningAgentOutput) -> str:
        proj_id = output.project_id or output.bom_id
        self._boms[proj_id] = output
        return proj_id

    async def save_bom_item(self, item: BOMItem, project_id: str) -> str:
        if project_id not in self._items:
            self._items[project_id] = []
        self._items[project_id].append(item)
        return f"{project_id}_{item.bom_item_id}"

    async def save_component_requirement(self, req: ComponentRequirementItem, project_id: str) -> str:
        if project_id not in self._requirements:
            self._requirements[project_id] = []
        self._requirements[project_id].append(req)
        return f"{project_id}_{req.requirement_id}"

    async def save_component_alternative(self, alt: ComponentAlternativeItem, project_id: str) -> str:
        if project_id not in self._alternatives:
            self._alternatives[project_id] = []
        self._alternatives[project_id].append(alt)
        return f"{project_id}_{alt.alternative_id}"

    async def save_bom_validation(self, val: BOMValidationItem, project_id: str) -> str:
        if project_id not in self._validations:
            self._validations[project_id] = []
        self._validations[project_id].append(val)
        return f"{project_id}_{val.validation_id}"

    async def save_bom_relationship(self, source_id: str, target_id: str, rel_type: str) -> str:
        self._relationships.append({"source": source_id, "target": target_id, "relationship": rel_type})
        return f"{source_id}->{rel_type}->{target_id}"

    async def get_bom(self, project_id: str) -> Optional[ComponentPlanningAgentOutput]:
        return self._boms.get(project_id)
