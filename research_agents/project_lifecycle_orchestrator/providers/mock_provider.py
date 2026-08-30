"""
Deterministic mock reasoning provider for testing ProjectLifecycleOrchestrator.
"""

from research_agents.project_lifecycle_orchestrator.providers.base import ReasoningProvider


class MockOrchestratorProvider(ReasoningProvider):
    """Deterministic mock provider returning structured orchestration reasoning."""

    async def reason(self, prompt: str, system_prompt: str = "") -> str:
        return "Deterministic orchestration analysis: graph state evaluated, dependencies verified, next action identified."
