"""
Abstract reasoning provider for ProjectLifecycleOrchestrator (Section 48).
"""

from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    """Abstract interface for Bedrock / reasoning synthesis in orchestration decisions."""

    @abstractmethod
    async def reason(self, prompt: str, system_prompt: str = "") -> str:
        """Invokes reasoning model for complex failure classification or human summarization."""
        pass
