"""
Mock reasoning provider for offline testing and deterministic verification.
"""

from research_agents.engineering_execution_agent.providers.base import ReasoningProvider


class MockExecutionProvider(ReasoningProvider):
    """Deterministic mock provider returning structured execution analysis."""

    async def analyze_task(self, prompt: str, system_prompt: str = "") -> str:
        return "Execution task verified against architectural invariants. Ready for tool dispatch under ArmorIQ."
