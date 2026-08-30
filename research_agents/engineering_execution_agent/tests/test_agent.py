"""
End-to-end unit and integration tests for EngineeringExecutionAgent (Agent #11).
"""

import tempfile
import pytest

from research_agents.engineering_execution_agent.agent import EngineeringExecutionAgent
from research_agents.engineering_execution_agent.armoriq.mock_client import MockArmorIQClient
from research_agents.engineering_execution_agent.providers.mock_provider import MockExecutionProvider
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionAgentInput,
    ExecutionTask,
)


@pytest.mark.asyncio
async def test_engineering_execution_agent_successful_run():
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = EngineeringExecutionAgent(
            armoriq_client=MockArmorIQClient(),
            reasoning_provider=MockExecutionProvider(),
            project_root_dir=tmp_dir,
        )

        input_data = EngineeringExecutionAgentInput(
            project={"title": "SAR Drone Execution Test", "project_id": "proj_sar_001"},
            implementation_plan={
                "tasks": [
                    {
                        "task_id": "TASK-001",
                        "title": "Create Lepton Driver",
                        "target_file": "firmware/sensors/lepton.py",
                        "file_content": "# Lepton Driver\n",
                        "allowed_paths": ["firmware/sensors/**"],
                        "allowed_tools": ["filesystem"],
                        "allowed_operations": ["create"],
                    }
                ]
            },
            validation={"verdict": "READY"},
            authorized_execution=AuthorizedExecution(
                authorization_id="AUTH-01",
                allowed_tasks=["TASK-001"],
                allowed_tools=["filesystem"],
                allowed_paths=["firmware/sensors/**"],
                allowed_operations=["read", "create"],
            ),
        )

        output = await agent.run(input_data)
        assert output.status == "success"
        assert len(output.completed_tasks) == 1
        assert len(output.tool_calls) == 1
        assert len(output.audit_trail) == 1
        assert len(output.execution_graph.nodes) >= 4
        assert "# Engineering Execution Report" in output.structured_report_markdown


@pytest.mark.asyncio
async def test_engineering_execution_agent_blocked_by_validation_gate():
    agent = EngineeringExecutionAgent(
        armoriq_client=MockArmorIQClient(),
        reasoning_provider=MockExecutionProvider(),
    )

    input_data = EngineeringExecutionAgentInput(
        project={"title": "SAR Drone Blocked", "project_id": "proj_sar_001"},
        implementation_plan={"tasks": [{"task_id": "TASK-001", "title": "Task"}]},
        validation={"verdict": "BLOCKED", "critical_failures": ["RULE-ELEC-001"]},
        authorized_execution=AuthorizedExecution(
            authorization_id="AUTH-01",
            allowed_tasks=["TASK-001"],
        ),
    )

    output = await agent.run(input_data)
    assert output.status == "blocked"
    assert len(output.completed_tasks) == 0
    assert "BLOCKED" in output.structured_report_markdown


def test_engineering_execution_agent_sync_and_adk_capabilities():
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = EngineeringExecutionAgent(
            armoriq_client=MockArmorIQClient(),
            project_root_dir=tmp_dir,
        )

        auth = AuthorizedExecution(
            authorization_id="AUTH-01",
            allowed_tasks=["TASK-001"],
            allowed_tools=["filesystem"],
            allowed_paths=["firmware/**"],
        )

        task = ExecutionTask(
            task_id="TASK-001",
            title="ADK Task Test",
            target_file="firmware/test.py",
            file_content="# ADK Test",
            allowed_paths=["firmware/**"],
            allowed_tools=["filesystem"],
        )

        # ADK Capability: validate_task_scope
        assert agent.validate_task_scope("TASK-001", auth) is True
        assert agent.validate_task_scope("TASK-999", auth) is False

        # ADK Capability: capture_execution_plan
        plan = agent.capture_execution_plan("Test plan")
        assert plan.get("receipt_id") is not None

        # ADK Capability: stop_execution
        stop_res = agent.stop_execution("exec_01")
        assert stop_res["status"] == "execution_stopped"
