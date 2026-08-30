"""
Scoped Git tool (Section 28).
Default: read-only (status, diff). Commit and push require explicit authorization.
"""

import os
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional
from research_agents.engineering_execution_agent.tools.base import BaseExecutionTool


class ScopedGitTool(BaseExecutionTool):
    """Executes authorized git versioning operations."""

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or os.getcwd()).resolve()

    @property
    def tool_name(self) -> str:
        return "git"

    def execute(
        self,
        operation: str,
        commit_message: Optional[str] = None,
        allowed_operations: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        allowed_ops = allowed_operations or ["status", "diff", "log"]

        if operation not in allowed_ops:
            raise PermissionError(
                f"Git operation '{operation}' is not authorized. Allowed: {allowed_ops}"
            )

        cmd: List[str] = ["git"]
        if operation == "status":
            cmd.extend(["status", "--porcelain"])
        elif operation == "diff":
            cmd.append("diff")
        elif operation == "commit":
            cmd.extend(["commit", "-m", commit_message or "Automated execution commit"])
        elif operation == "push":
            cmd.append("push")
        else:
            cmd.append(operation)

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.project_root_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "operation": operation,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "status": "success" if proc.returncode == 0 else "failed",
            }
        except Exception as e:
            return {"operation": operation, "exit_code": -1, "status": "error", "stderr": str(e)}
