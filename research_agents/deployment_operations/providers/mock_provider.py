"""
Deterministic Mock reasoning provider for testing and offline execution.
"""

from typing import Optional
from research_agents.deployment_operations.providers.base import BaseReasoningProvider


class MockReasoningProvider(BaseReasoningProvider):
    """Deterministic mock provider."""

    def __init__(self, canned_response: Optional[str] = None):
        self.canned_response = canned_response

    async def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> str:
        if self.canned_response:
            return self.canned_response
        return (
            "Deterministic Operational Evaluation: Deployment prerequisites validated. "
            "All commissioning gates must pass before switching to active operational mode. "
            "Rollback triggers configured."
        )
