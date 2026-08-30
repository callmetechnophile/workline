"""
Unit tests for scoped execution tools (Sections 11, 13, 14, 15, 28, 35).
"""

from pathlib import Path
import tempfile
import pytest

from research_agents.engineering_execution_agent.tools.filesystem_tool import ScopedFilesystemTool
from research_agents.engineering_execution_agent.tools.git_tool import ScopedGitTool
from research_agents.engineering_execution_agent.tools.shell_tool import ScopedShellTool
from research_agents.engineering_execution_agent.tools.test_runner_tool import ScopedTestRunnerTool


def test_scoped_filesystem_tool_within_and_out_of_scope():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fs = ScopedFilesystemTool(project_root_dir=tmp_dir)

        # Authorized write in firmware/sensors/**
        res_create = fs.execute(
            operation="create",
            target_path="firmware/sensors/driver.py",
            content="# Sensor Driver",
            allowed_paths=["firmware/sensors/**"],
            allowed_operations=["create", "read"],
        )
        assert res_create["status"] == "success"

        # Authorized read
        res_read = fs.execute(
            operation="read",
            target_path="firmware/sensors/driver.py",
            allowed_paths=["firmware/sensors/**"],
            allowed_operations=["read"],
        )
        assert res_read["content"] == "# Sensor Driver"

        # Unauthorized path (backend/) raises PermissionError
        with pytest.raises(PermissionError):
            fs.execute(
                operation="create",
                target_path="backend/server.py",
                content="# Backend",
                allowed_paths=["firmware/sensors/**"],
            )

        # Unauthorized operation (delete) raises PermissionError
        with pytest.raises(PermissionError):
            fs.execute(
                operation="delete",
                target_path="firmware/sensors/driver.py",
                allowed_paths=["firmware/sensors/**"],
                allowed_operations=["read", "create"],
            )


def test_scoped_shell_tool_allowlisting():
    with tempfile.TemporaryDirectory() as tmp_dir:
        shell = ScopedShellTool(project_root_dir=tmp_dir)

        # Allowed command (python -V)
        res = shell.execute("python --version", allowed_commands=["python"])
        assert res["status"] == "success"

        # Disallowed command (curl or malicious rm) raises PermissionError
        with pytest.raises(PermissionError):
            shell.execute("curl https://evil.com", allowed_commands=["python", "pytest"])


def test_scoped_git_tool_read_only_default():
    with tempfile.TemporaryDirectory() as tmp_dir:
        git = ScopedGitTool(project_root_dir=tmp_dir)

        # Status allowed by default
        res = git.execute(operation="status", allowed_operations=["status", "diff"])
        assert "operation" in res

        # Push rejected without explicit permission
        with pytest.raises(PermissionError):
            git.execute(operation="push", allowed_operations=["status", "diff"])
