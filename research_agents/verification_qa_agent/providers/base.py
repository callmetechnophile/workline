"""
Abstract reasoning provider interface for VerificationQAAgent.
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for LLM synthesis and QA analysis."""

    @abstractmethod
    async def analyze_qa(self, prompt: str, system_prompt: str = "") -> str:
        """Invokes reasoning model for failure interpretation or architecture reasoning."""
        pass
