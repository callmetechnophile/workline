"""
Abstract reasoning provider for EngineeringChangeControlAgent (Section 59).
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for Bedrock / LLM change explanation and risk reasoning."""

    @abstractmethod
    async def explain_change(self, prompt: str, system_prompt: str = "") -> str:
        """Explains engineering impact and risk tradeoffs."""
        pass
