"""
Deterministic Mock reasoning provider for testing and offline environments.
"""

from typing import Optional
from research_agents.cost_supply_chain.providers.base import BaseReasoningProvider


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
            "Heuristic Evaluation: The proposed configuration demonstrates optimal cost "
            "efficiency when target volumes exceed the calculated tooling breakeven threshold. "
            "Supply chain risks should be mitigated via dual-sourcing."
        )
