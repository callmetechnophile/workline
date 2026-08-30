"""
Deterministic mock reasoning provider for testing EngineeringComplianceAgent.
"""

from research_agents.engineering_compliance.providers.base import ReasoningProvider


class MockComplianceProvider(ReasoningProvider):
    """Deterministic mock provider returning compliance explanations."""

    async def explain_compliance(self, prompt: str, system_prompt: str = "") -> str:
        return "Deterministic design rule evaluation confirmed compliance against validated electrical and interface specifications."
