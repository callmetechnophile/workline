"""
Abstract reasoning provider for EngineeringSimulationAgent (Section 69).
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for Bedrock / LLM simulation summarization and what-if interpretation."""

    @abstractmethod
    async def explain_simulation(self, prompt: str, system_prompt: str = "") -> str:
        """Explains computational models, sweep results, and what-if trade-offs."""
        pass
