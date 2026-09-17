"""Tests for reasoning providers."""
import pytest
from research_agents.project_execution_agent.providers.mock_provider import MockProjectExecutionProvider

@pytest.mark.asyncio
async def test_mock_provider():
    provider = MockProjectExecutionProvider()
    wbs = await provider.generate_work_breakdown(
        project_context={"project_id": "p1", "title": "Drone"},
        architecture={},
        bom={},
        validation={},
    )
    assert len(wbs) == 4
    total_tasks = sum(len(wp.tasks) for wp in wbs)
    assert total_tasks >= 5
