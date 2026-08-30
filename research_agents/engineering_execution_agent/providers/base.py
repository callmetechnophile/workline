"""
Abstract reasoning provider interface for EngineeringExecutionAgent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ReasoningProvider(ABC):
    """Abstract interface for LLM synthesis and execution analysis."""

    @abstractmethod
    async def analyze_task(self, prompt: str, system_prompt: str = "") -> str:
        """Invokes reasoning model for execution task analysis."""
        pass
