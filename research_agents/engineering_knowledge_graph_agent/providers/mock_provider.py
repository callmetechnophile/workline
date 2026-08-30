"""
Deterministic mock reasoning provider for offline testing.
"""

from research_agents.engineering_knowledge_graph_agent.providers.base import ReasoningProvider


class MockGraphProvider(ReasoningProvider):
    """Deterministic mock provider returning structured graph explanations."""

    async def explain_graph(self, prompt: str, system_prompt: str = "") -> str:
        return "Graph analysis verified end-to-end requirement lineage through architecture, BOM, and execution evidence."
