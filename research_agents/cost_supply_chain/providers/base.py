"""
Base abstract class for LLM / Reasoning providers in Agent #25.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseReasoningProvider(ABC):
    """Abstract interface for LLM reasoning."""

    @abstractmethod
    async def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> str:
        """Generate text completion from LLM."""
        pass
