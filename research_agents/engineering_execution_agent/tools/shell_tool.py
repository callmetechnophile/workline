"""
Scoped shell execution tool with command allowlisting (Sections 15, 16, 80).
"""

import os
from pathlib import Path
import shlex
import subprocess
from typing import Any, Dict, List, Optional
from research_agents.engineering_execution_agent.tools.base import BaseExecutionTool


class ScopedShellTool(BaseExecutionTool):
    """Executes validated, allowlisted shell commands."""

    # Baseline safe command allowlist prefixes
    DEFAULT_ALLOWLIST = [
        "python",
        "python3",
        "pytest",
        "uv",
        "node",
        "npm test",
        "npm run build",
        "gcc",
        "g++",
        "cmake",
        "make",
        "git status",
        "git diff",
        "git log",
    ]

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or os.getcwd()).resolve()

    @property
    def tool_name(self) -> str:
        return "shell"

    def is_command_authorized(
        self,
        command: str,
        allowed_commands: Optional[List[str]] = None,
    ) -> bool:
        """
        Validates whether command matches allowed patterns or baseline safe tools.
        """
        allowlist = allowed_commands if allowed_commands is not None else self.DEFAULT_ALLOWLIST
        cmd_clean = command.strip()

        # Reject dangerous shell injection tokens
        dangerous_tokens = [";", "&&", "||", "|", "`", "$(", ">", ">>"]
        for token in dangerous_tokens:
            if token in cmd_clean:
                # Check if complex chaining is explicitly allowed or rejected
                return False

        # Check against allowlist
        for allowed in allowlist:
            if cmd_clean.startswith(allowed):
                return True

        return False

    def execute(
        self,
        command: str,
        allowed_commands: Optional[List[str]] = None,
        timeout_sec: int = 30,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Parses and executes authorized command synchronously.
        """
        if not self.is_command_authorized(command, allowed_commands):
            raise PermissionError(
                f"Command '{command}' is not in the authorized command allowlist."
            )

        try:
            # Parse command safely
            args = shlex.split(command, posix=(os.name != "nt"))
            proc = subprocess.run(
                args,
                cwd=str(self.project_root_dir),
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            return {
                "command": command,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "status": "success" if proc.returncode == 0 else "failed",
            }
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout_sec}s",
                "status": "timeout",
            }
        except Exception as e:
            return {
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "status": "error",
            }
