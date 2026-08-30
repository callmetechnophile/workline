"""
Scoped test runner execution tool (Section 35).
"""

import os
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional
from research_agents.engineering_execution_agent.tools.base import BaseExecutionTool


class ScopedTestRunnerTool(BaseExecutionTool):
    """Executes authorized unit/integration test suites."""

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or os.getcwd()).resolve()

    @property
    def tool_name(self) -> str:
        return "test_runner"

    def execute(
        self,
        test_path: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        timeout_sec: int = 60,
        **kwargs,
    ) -> Dict[str, Any]:
        cmd = ["pytest"]
        if test_path:
            cmd.append(test_path)
        if extra_args:
            cmd.extend(extra_args)

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.project_root_dir),
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            return {
                "test_command": " ".join(cmd),
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "passed": proc.returncode == 0,
                "status": "success" if proc.returncode == 0 else "failed",
            }
        except subprocess.TimeoutExpired:
            return {
                "test_command": " ".join(cmd),
                "exit_code": -1,
                "passed": False,
                "status": "timeout",
                "stderr": f"Tests timed out after {timeout_sec}s",
            }
        except Exception as e:
            return {
                "test_command": " ".join(cmd),
                "exit_code": -1,
                "passed": False,
                "status": "error",
                "stderr": str(e),
            }
