"""
Deterministic mock reasoning provider for testing EngineeringCopilotAgent.
"""

from research_agents.engineering_copilot.providers.base import ReasoningProvider


class MockCopilotProvider(ReasoningProvider):
    """Deterministic mock provider returning evidence-grounded answers."""

    async def generate_answer(self, prompt: str, system_prompt: str = "") -> str:
        return "The FLIR Lepton 3.5 thermal sensor (MPN 500-0771-01) was selected to fulfill REQ-SAR-001 based on decision DEC-001."
