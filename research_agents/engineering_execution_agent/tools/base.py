"""
Abstract base class for scoped execution tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseExecutionTool(ABC):
    """Abstract interface for all execution tools governed by ArmorIQ."""

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Name of the tool (e.g. 'filesystem', 'shell', 'test_runner')."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Executes the specific authorized operation."""
        pass
