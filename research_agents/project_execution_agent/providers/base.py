"""
Abstract base reasoning provider for ProjectExecutionAgent (Agent #10).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from research_agents.project_execution_agent.schemas import WorkPackage


class ReasoningProvider(ABC):
    """Abstract interface for implementation planning intelligence."""

    @abstractmethod
    async def generate_work_breakdown(
        self,
        project_context: Dict[str, Any],
        architecture: Dict[str, Any],
        bom: Dict[str, Any],
        validation: Dict[str, Any],
    ) -> List[WorkPackage]:
        """Generate structured work packages and planning tasks."""
        pass
