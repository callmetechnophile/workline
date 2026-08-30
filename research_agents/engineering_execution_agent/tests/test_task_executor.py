"""
Unit tests for TaskExecutor service (Sections 24, 25, 26, 41, 42).
"""

import tempfile
from research_agents.engineering_execution_agent.armoriq.mock_client import MockArmorIQClient
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionContext,
    ExecutionTask,
)
from research_agents.engineering_execution_agent.services.change_detector import ChangeDetector
from research_agents.engineering_execution_agent.services.task_executor import TaskExecutor
from research_agents.engineering_execution_agent.tools.filesystem_tool import ScopedFilesystemTool


def test_task_executor_dependency_enforcement():
    with tempfile.TemporaryDirectory() as tmp_dir:
        mock_armoriq = MockArmorIQClient()
        executor = TaskExecutor(
            armoriq_client=mock_armoriq,
            change_detector=ChangeDetector(tmp_dir),
            fs_tool=ScopedFilesystemTool(tmp_dir),
        )

        auth = AuthorizedExecution(
            authorization_id="AUTH-01",
            allowed_tasks=["TASK-001", "TASK-002"],
            allowed_paths=["firmware/**"],
            allowed_tools=["filesystem"],
            allowed_operations=["create", "modify"],
        )
        context = EngineeringExecutionContext(project_id="proj_01")

        # TASK-002 depends on TASK-001. TASK-001 will fail due to out of scope target file.
        task1 = ExecutionTask(
            task_id="TASK-001",
            title="Task 1 (Out of scope path)",
            target_file="backend/unauthorized.py",
            file_content="# code",
            allowed_paths=["backend/**"],
        )
        task2 = ExecutionTask(
            task_id="TASK-002",
            title="Task 2 (Dependent on Task 1)",
            target_file="firmware/valid.py",
            dependencies=["TASK-001"],
            allowed_paths=["firmware/**"],
        )

        completed, failed, blocked, denied, tool_calls, receipts, audit, changed = executor.execute_tasks(
            tasks=[task1, task2],
            auth=auth,
            context=context,
            architecture={},
            bom={},
        )

        # Task 1 denied (out of scope), Task 2 blocked by dependency
        assert len(denied) == 1
        assert denied[0]["task_id"] == "TASK-001"
        assert len(blocked) == 1
        assert blocked[0]["task_id"] == "TASK-002"
        assert "DEPENDENCY_BLOCKED" in blocked[0]["reason"]
