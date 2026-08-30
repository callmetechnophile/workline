"""
Abstract reasoning provider for EngineeringCopilotAgent (Section 43).
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for Bedrock / LLM conversational explanation."""

    @abstractmethod
    async def generate_answer(self, prompt: str, system_prompt: str = "") -> str:
        """Generates evidence-grounded answer for engineering queries."""
        pass
