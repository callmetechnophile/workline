"""
Deterministic mock reasoning provider for testing EngineeringSimulationAgent.
"""

from research_agents.engineering_simulation.providers.base import ReasoningProvider


class MockSimulationProvider(ReasoningProvider):
    """Deterministic mock provider returning simulation explanations."""

    async def explain_simulation(self, prompt: str, system_prompt: str = "") -> str:
        return "Deterministic numerical simulation confirmed that power dissipation and thermal metrics remain within safe operating bounds."
