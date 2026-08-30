"""
Scoped filesystem execution tool (Sections 13, 14, 80).
Enforces path boundaries, path normalization, and operation permissions.
"""

from fnmatch import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from research_agents.engineering_execution_agent.tools.base import BaseExecutionTool


class ScopedFilesystemTool(BaseExecutionTool):
    """Safely executes filesystem operations within explicitly authorized path boundaries."""

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or os.getcwd()).resolve()

    @property
    def tool_name(self) -> str:
        return "filesystem"

    def is_path_authorized(self, rel_or_abs_path: str, allowed_paths: List[str]) -> bool:
        """
        Validates path normalization, glob match, and prevents path traversal (../).
        """
        if not allowed_paths:
            return False

        # If "**" wildcard is in allowed_paths, all project-internal paths are valid
        if "**" in allowed_paths or "*" in allowed_paths:
            resolved_target = (self.project_root_dir / rel_or_abs_path).resolve()
            return str(resolved_target).startswith(str(self.project_root_dir))

        # Check for path traversal attacks
        if ".." in rel_or_abs_path:
            return False

        norm_path = rel_or_abs_path.replace("\\", "/").strip("./")
        
        # Check against allowed globs
        for pattern in allowed_paths:
            clean_pat = pattern.replace("\\", "/").strip("./")
            if fnmatch(norm_path, clean_pat) or fnmatch(f"/{norm_path}", clean_pat):
                return True
            if clean_pat.endswith("/**") and norm_path.startswith(clean_pat[:-3]):
                return True

        return False

    def execute(
        self,
        operation: str,
        target_path: str,
        content: Optional[str] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_operations: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Executes read, create, modify, or delete within allowed path scope.
        """
        allowed_paths = allowed_paths or []
        allowed_operations = allowed_operations or ["read", "create", "modify"]

        # 1. Operation check
        if operation not in allowed_operations:
            raise PermissionError(
                f"Filesystem operation '{operation}' is not authorized. Allowed: {allowed_operations}"
            )

        # 2. Path authorization check
        if not self.is_path_authorized(target_path, allowed_paths):
            raise PermissionError(
                f"Path '{target_path}' is outside authorized filesystem scope: {allowed_paths}"
            )

        # Resolve full path safely within project root
        target_file = (self.project_root_dir / target_path).resolve()

        # Final check: target must be inside project_root_dir
        if not str(target_file).startswith(str(self.project_root_dir)):
            raise PermissionError(
                f"Path traversal detected: '{target_file}' escapes root '{self.project_root_dir}'"
            )

        if operation == "read":
            if not target_file.exists():
                raise FileNotFoundError(f"File not found: {target_file}")
            text = target_file.read_text(encoding="utf-8")
            return {"operation": "read", "path": str(target_path), "content": text, "bytes": len(text)}

        elif operation in ("create", "modify"):
            target_file.parent.mkdir(parents=True, exist_ok=True)
            content_to_write = content or ""
            target_file.write_text(content_to_write, encoding="utf-8")
            return {
                "operation": operation,
                "path": str(target_path),
                "bytes_written": len(content_to_write),
                "status": "success",
            }

        elif operation == "delete":
            if target_file.exists():
                if target_file.is_file():
                    target_file.unlink()
                elif target_file.is_dir():
                    import shutil
                    shutil.rmtree(target_file)
            return {"operation": "delete", "path": str(target_path), "status": "deleted"}

        else:
            raise ValueError(f"Unknown filesystem operation: {operation}")
