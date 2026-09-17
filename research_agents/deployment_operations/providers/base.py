"""
Abstract LLM/Reasoning provider base for Agent #26.
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
        """Generate completion from provider."""
        pass
