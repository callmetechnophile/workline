"""
End-to-end unit and integration tests for DeepResearchAgent.
"""

import pytest
from research_agents.deep_research_agent.agent import DeepResearchAgent
from research_agents.deep_research_agent.providers.base import (
    ProviderTimeoutError,
    ReasoningProvider,
)
from research_agents.deep_research_agent.providers.mock_provider import MockReasoningProvider
from research_agents.deep_research_agent.schemas import (
    DeepResearchAgentInput,
    ProjectMeta,
)


class FailingReasoningProvider(ReasoningProvider):
    async def generate(self, prompt: str, system_prompt=None, max_tokens=None, temperature=None):
        raise ProviderTimeoutError("bedrock", "Reasoning request timed out.")

    async def generate_structured(self, prompt: str, schema, system_prompt=None):
        raise ProviderTimeoutError("bedrock", "Structured synthesis timed out.")


@pytest.mark.asyncio
async def test_deep_research_agent_successful_run():
    agent = DeepResearchAgent(reasoning_provider=MockReasoningProvider())
    input_data = DeepResearchAgentInput(
        project=ProjectMeta(
            title="Autonomous Search and Rescue Drone",
            engineering_domain="Robotics / Edge AI",
            objectives=["thermal human detection"],
            components=["Jetson Orin Nano", "FLIR Lepton 3.5"],
        ),
        research_papers=[
            {"paper_id": "paper_01", "title": "Thermal Drone Vision", "abstract": "45 FPS thermal detection on Jetson."}
        ],
        web_sources=[
            {"source_id": "web_01", "title": "Jetson Orin Specs", "description": "40 TOPS AI compute at 15 W."}
        ],
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert output.project.title == "Autonomous Search and Rescue Drone"
    assert output.executive_summary != ""
    assert len(output.component_trade_studies) >= 1
    assert len(output.extracted_claims) >= 1
    assert len(output.recommendations) >= 1
    assert len(output.evidence_used) >= 2
    assert "# Engineering Research Synthesis" in output.structured_markdown_report


@pytest.mark.asyncio
async def test_deep_research_agent_error_handling():
    agent = DeepResearchAgent(reasoning_provider=FailingReasoningProvider())
    input_data = DeepResearchAgentInput(
        project=ProjectMeta(title="Failure Test Drone"),
    )

    output = await agent.run(input_data)

    assert output.status == "error"
    assert len(output.errors) > 0
    assert output.errors[0].code == "TIMEOUT"
    assert output.errors[0].retryable is True


def test_deep_research_agent_sync_execution():
    agent = DeepResearchAgent(reasoning_provider=MockReasoningProvider())
    input_data = DeepResearchAgentInput(
        project=ProjectMeta(title="Sync Run Drone"),
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert output.executive_summary != ""
