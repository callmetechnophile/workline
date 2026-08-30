"""
Mock reasoning provider for offline QA testing and deterministic verification.
"""

from research_agents.verification_qa_agent.providers.base import ReasoningProvider


class MockQAProvider(ReasoningProvider):
    """Deterministic mock provider returning structured QA explanations."""

    async def analyze_qa(self, prompt: str, system_prompt: str = "") -> str:
        return "QA verification confirmed all test cases, cryptographic receipts, and architectural invariants."
