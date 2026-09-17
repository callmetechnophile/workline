"""End-to-end unit and integration tests for ProjectExecutionAgent."""
import pytest
from research_agents.project_execution_agent.agent import ProjectExecutionAgent
from research_agents.project_execution_agent.providers.mock_provider import MockProjectExecutionProvider
from research_agents.project_execution_agent.schemas import ProjectExecutionAgentInput

@pytest.mark.asyncio
async def test_agent_run_success():
    agent = ProjectExecutionAgent(reasoning_provider=MockProjectExecutionProvider())
    inp = ProjectExecutionAgentInput(
        project={"project_id": "proj_drone_001", "title": "Autonomous SAR Drone", "engineering_domain": "Robotics"},
        architecture={"subsystems": ["ThermalImaging", "Navigation"]},
        bom={"items": [{"component_id": "c1", "name": "FLIR"}]},
        validation={"verdict": "VERIFIED"},
    )
    output = await agent.run(inp)
    assert output.status == "success"
    assert output.execution_readiness is True
    assert output.work_package_count >= 3
    assert output.task_count >= 5
    assert len(output.structured_markdown_report) > 100
    assert "# Implementation Plan" in output.structured_markdown_report

def test_agent_run_sync():
    agent = ProjectExecutionAgent(reasoning_provider=MockProjectExecutionProvider())
    inp = ProjectExecutionAgentInput(
        project_id="proj_sync_001",
        title="Edge Vision System",
        engineering_domain="Computer Vision",
    )
    output = agent.run_sync(inp)
    assert output.status == "success"
    assert output.plan_id.startswith("PLAN-")
