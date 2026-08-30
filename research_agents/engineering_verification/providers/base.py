"""
Abstract reasoning provider for EngineeringVerificationAgent (Section 75).
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for Bedrock / LLM verification summarization and failure explanation."""

    @abstractmethod
    async def explain_verification(self, prompt: str, system_prompt: str = "") -> str:
        """Explains test results, failure categories, and verification evidence."""
        pass
