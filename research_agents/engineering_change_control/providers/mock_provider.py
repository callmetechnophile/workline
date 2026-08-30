"""
Deterministic mock reasoning provider for testing EngineeringChangeControlAgent.
"""

from research_agents.engineering_change_control.providers.base import ReasoningProvider


class MockChangeControlProvider(ReasoningProvider):
    """Deterministic mock provider returning change justification summaries."""

    async def explain_change(self, prompt: str, system_prompt: str = "") -> str:
        return "Controlled engineering change replaces component with verified alternative, preserving validated interfaces and trigger revalidation."
