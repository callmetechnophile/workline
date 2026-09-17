"""Tests for dashboard service and file exports."""
import pytest
from research_agents.deployment_operations.agent import DeploymentOpsAgent
from research_agents.deployment_operations.schemas import DeploymentOpsInput, SystemType
from research_agents.deployment_operations.services.dashboard_service import DashboardService
from research_agents.deployment_operations.services.file_exporter import FileExporter


@pytest.mark.asyncio
async def test_dashboard_and_export():
    agent = DeploymentOpsAgent()
    inp = DeploymentOpsInput(project_id="PROJ-EXP", system_id="SYS-EXP", system_type=SystemType.HYBRID)
    out = await agent.run(inp)

    dash_service = DashboardService()
    posture = dash_service.compile_posture(out)
    assert posture["project_id"] == "PROJ-EXP"
    assert posture["deployment_steps_count"] > 0

    exporter = FileExporter()
    json_str = exporter.to_json(out)
    assert "SYS-EXP" in json_str

    csv_str = exporter.to_csv_deployment_plan(out)
    assert "Step Number,Title" in csv_str
