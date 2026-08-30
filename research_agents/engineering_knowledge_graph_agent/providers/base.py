"""
Abstract reasoning provider interface for EngineeringKnowledgeGraphAgent.
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for LLM synthesis and semantic graph explanation."""

    @abstractmethod
    async def explain_graph(self, prompt: str, system_prompt: str = "") -> str:
        """Invokes reasoning model for natural-language explanation of graph queries."""
        pass
