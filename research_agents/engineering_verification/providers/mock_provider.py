"""
Deterministic mock reasoning provider for testing EngineeringVerificationAgent.
"""

from research_agents.engineering_verification.providers.base import ReasoningProvider


class MockVerificationProvider(ReasoningProvider):
    """Deterministic mock provider returning verification explanations."""

    async def explain_verification(self, prompt: str, system_prompt: str = "") -> str:
        return "Deterministic test execution confirmed that all measured telemetry parameters satisfy requirement acceptance criteria."
