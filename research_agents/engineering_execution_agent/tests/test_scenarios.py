"""
Integration test scenarios mandated by specification (Sections 68–79).
"""

import tempfile
import pytest

from research_agents.engineering_execution_agent.agent import EngineeringExecutionAgent
from research_agents.engineering_execution_agent.armoriq.mock_client import MockArmorIQClient
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionAgentInput,
    ExecutionTask,
)


@pytest.mark.asyncio
async def test_scenario_68_authorized_task_success():
    """Section 68: Authorized task modifies firmware/sensors/sensor_driver.py successfully."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = EngineeringExecutionAgent(
            armoriq_client=MockArmorIQClient(),
            project_root_dir=tmp_dir,
        )

        input_data = EngineeringExecutionAgentInput(
            project={"title": "SAR Drone Execution", "project_id": "proj_01"},
            implementation_plan={
                "tasks": [
                    {
                        "task_id": "TASK-001",
                        "title": "Implement sensor driver",
                        "task_type": "firmware",
                        "target_file": "firmware/sensors/sensor_driver.py",
                        "file_content": "# Sensor Driver Code\n",
                        "allowed_paths": ["firmware/sensors/**"],
                        "allowed_tools": ["filesystem"],
                        "allowed_operations": ["create", "modify"],
                    }
                ]
            },
            validation={"verdict": "READY"},
            authorized_execution=AuthorizedExecution(
                authorization_id="AUTH-01",
                allowed_tasks=["TASK-001"],
                allowed_tools=["filesystem"],
                allowed_paths=["firmware/sensors/**"],
                allowed_operations=["read", "create", "modify"],
            ),
        )

        output = await agent.run(input_data)
        assert output.status == "success"
        assert len(output.completed_tasks) == 1
        assert len(output.tool_calls) == 1
        assert output.tool_calls[0].status == "success"


@pytest.mark.asyncio
async def test_scenario_69_out_of_scope_file_denied():
    """Section 69: Agent attempts to modify backend/server.py with only firmware/sensors/** scope -> DENIED."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = EngineeringExecutionAgent(
            armoriq_client=MockArmorIQClient(),
            project_root_dir=tmp_dir,
        )

        input_data = EngineeringExecutionAgentInput(
            project={"title": "SAR Drone", "project_id": "proj_01"},
            implementation_plan={
                "tasks": [
                    {
                        "task_id": "TASK-001",
                        "title": "Modify server backend",
                        "target_file": "backend/server.py",
                        "file_content": "# Out of scope server\n",
                    }
                ]
            },
            validation={"verdict": "READY"},
            authorized_execution=AuthorizedExecution(
                authorization_id="AUTH-01",
                allowed_tasks=["TASK-001"],
                allowed_tools=["filesystem"],
                allowed_paths=["firmware/sensors/**"],  # backend/ is excluded
            ),
        )

        output = await agent.run(input_data)
        assert output.status == "denied"
        assert len(output.denied_actions) == 1
        assert output.denied_actions[0]["status"] == "OUT_OF_SCOPE"


@pytest.mark.asyncio
async def test_scenario_70_out_of_scope_tool_denied():
    """Section 70: Agent attempts git push with only filesystem scope -> DENIED."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = EngineeringExecutionAgent(
            armoriq_client=MockArmorIQClient(),
            project_root_dir=tmp_dir,
        )

        input_data = EngineeringExecutionAgentInput(
            project={"title": "SAR Drone", "project_id": "proj_01"},
            implementation_plan={
                "tasks": [
                    {
                        "task_id": "TASK-001",
                        "title": "Push to remote git",
                        "allowed_tools": ["git.push"],
                    }
                ]
            },
            validation={"verdict": "READY"},
            authorized_execution=AuthorizedExecution(
                authorization_id="AUTH-01",
                allowed_tasks=["TASK-001"],
                allowed_tools=["filesystem"],  # git.push is excluded
            ),
        )

        output = await agent.run(input_data)
        assert output.status == "denied"
        assert len(output.denied_actions) == 1
        assert output.denied_actions[0]["status"] == "OUT_OF_SCOPE"


@pytest.mark.asyncio
async def test_scenario_72_expired_authority_denied():
    """Section 72: Expired authority -> DENIED."""
    agent = EngineeringExecutionAgent(armoriq_client=MockArmorIQClient())
    input_data = EngineeringExecutionAgentInput(
        project={"title": "SAR Drone", "project_id": "proj_01"},
        implementation_plan={"tasks": [{"task_id": "TASK-001", "title": "Task 1"}]},
        validation={"verdict": "READY"},
        authorized_execution=AuthorizedExecution(
            authorization_id="AUTH-EXP",
            allowed_tasks=["TASK-001"],
            expires_at="2020-01-01T00:00:00Z",
        ),
    )

    output = await agent.run(input_data)
    assert output.status == "denied"
    assert output.denied_actions[0]["status"] == "EXPIRED_AUTHORITY"


@pytest.mark.asyncio
async def test_scenario_74_dependency_blocked():
    """Section 74: Dependent task blocked when upstream task fails."""
    agent = EngineeringExecutionAgent(armoriq_client=MockArmorIQClient())
    input_data = EngineeringExecutionAgentInput(
        project={"title": "SAR Drone", "project_id": "proj_01"},
        implementation_plan={
            "tasks": [
                {"task_id": "TASK-001", "title": "Unlisted Task", "target_file": "backend/unauth.py"},
                {"task_id": "TASK-002", "title": "Dependent Task", "dependencies": ["TASK-001"]},
            ]
        },
        validation={"verdict": "READY"},
        authorized_execution=AuthorizedExecution(
            authorization_id="AUTH-01",
            allowed_tasks=["TASK-002"],  # TASK-001 not authorized
            allowed_paths=["firmware/**"],
        ),
    )

    output = await agent.run(input_data)
    assert len(output.blocked_tasks) == 1
    assert output.blocked_tasks[0]["task_id"] == "TASK-002"


@pytest.mark.asyncio
async def test_scenario_78_dry_run_executes_no_tools():
    """Section 78: Dry run validates plan and authority without calling tools."""
    agent = EngineeringExecutionAgent(armoriq_client=MockArmorIQClient())
    input_data = EngineeringExecutionAgentInput(
        project={"title": "SAR Drone Dry Run", "project_id": "proj_01"},
        implementation_plan={"tasks": [{"task_id": "TASK-001", "title": "Task 1"}]},
        validation={"verdict": "READY"},
        authorized_execution=AuthorizedExecution(
            authorization_id="AUTH-01",
            allowed_tasks=["TASK-001"],
            allowed_tools=["filesystem"],
            allowed_paths=["firmware/**"],
        ),
        dry_run=True,
    )

    output = await agent.run(input_data)
    assert output.status == "success"
    assert len(output.tool_calls) == 0  # Zero tools called in dry run
    assert output.completed_tasks[0]["status"] == "dry_run_verified"


@pytest.mark.asyncio
async def test_scenario_79_armoriq_unavailable_blocks_execution():
    """Section 79: When ArmorIQ is unavailable, execution is blocked without fallback."""
    mock_unavailable = MockArmorIQClient(simulate_unavailable=True)
    agent = EngineeringExecutionAgent(armoriq_client=mock_unavailable)

    input_data = EngineeringExecutionAgentInput(
        project={"title": "SAR Drone", "project_id": "proj_01"},
        implementation_plan={"tasks": [{"task_id": "TASK-001", "title": "Task 1"}]},
        validation={"verdict": "READY"},
        authorized_execution=AuthorizedExecution(
            authorization_id="AUTH-01",
            allowed_tasks=["TASK-001"],
        ),
    )

    with pytest.raises(RuntimeError, match="ArmorIQ authorization layer unavailable"):
        await agent.run(input_data)
