"""
Abstract reasoning provider for EngineeringComplianceAgent (Section 78).
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for Bedrock / LLM compliance summarization and rule explanation."""

    @abstractmethod
    async def explain_compliance(self, prompt: str, system_prompt: str = "") -> str:
        """Explains compliance evaluation results and regulatory requirements."""
        pass
