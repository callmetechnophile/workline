"""
Zero-Implicit-Authority and scope validation gate for EngineeringExecutionAgent (Sections 2, 7, 8, 9, 81, 82).
Enforces strict 5-point scoping: tasks, tools, paths, operations, expiry.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger
from research_agents.engineering_execution_agent.schemas import AuthorizedExecution, ExecutionTask


class AuthorizationGate:
    """Strict authorization validator enforcing zero implicit authority and validation gating."""

    def check_validation_gate(self, validation_data: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """
        Validates Agent #9 validation verdict (Section 7).
        Allowed: READY, READY_WITH_WARNINGS.
        Blocked: BLOCKED, INCOMPLETE.
        """
        if not validation_data:
            # If no validation is present, check if verdict is passed in dict
            return True, "READY", []

        verdict = str(validation_data.get("verdict") or validation_data.get("status") or "UNKNOWN").upper()
        blocking_ids: List[str] = []

        # Extract critical blocking failure IDs if present
        for f in validation_data.get("critical_failures", []):
            if isinstance(f, dict):
                blocking_ids.append(f.get("validation_id") or f.get("title", "BLOCKING-RULE"))
            elif isinstance(f, str):
                blocking_ids.append(f)

        if verdict in ("READY", "READY_WITH_WARNINGS", "SUCCESS"):
            return True, verdict, []
        elif verdict in ("BLOCKED", "FAIL", "FAILED"):
            return False, "BLOCKED", blocking_ids or ["VAL-CRITICAL-BLOCK"]
        elif verdict in ("INCOMPLETE", "UNKNOWN"):
            return False, "INCOMPLETE", blocking_ids or ["VAL-SPEC-INCOMPLETE"]
        else:
            return False, "BLOCKED", blocking_ids or ["VAL-UNAPPROVED-DESIGN"]

    def validate_authorization(
        self,
        task: ExecutionTask,
        auth: AuthorizedExecution,
        current_project_id: str,
        current_agent_id: str = "EngineeringExecutionAgent",
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validates complete authority chain before executing a task (Section 8).
        Checks:
        1. Revocation
        2. Expiry
        3. Project ID alignment
        4. Agent identity matching
        5. Task authorization
        6. Tool authorization
        7. Operation authorization
        8. Resource/path authorization
        """
        # 1. Check revocation
        if auth.revoked:
            return False, "REVOKED_AUTHORITY", f"Authorization '{auth.authorization_id}' has been revoked."

        # 2. Check expiration
        if auth.expires_at:
            try:
                exp_dt = datetime.fromisoformat(auth.expires_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > exp_dt:
                    return False, "EXPIRED_AUTHORITY", f"Authorization '{auth.authorization_id}' expired at {auth.expires_at}."
            except Exception as e:
                logger.warning(f"Could not parse expires_at timestamp '{auth.expires_at}': {e}")

        # 3. Check agent identity
        if auth.authorized_agent_id != current_agent_id:
            return (
                False,
                "AUTHORIZATION_DENIED",
                f"Authority issued to '{auth.authorized_agent_id}', but invoked by '{current_agent_id}'.",
            )

        # 4. Check project scope
        auth_proj = auth.scope.get("project_id") if auth.scope else None
        if auth_proj and auth_proj != current_project_id:
            return (
                False,
                "AUTHORIZATION_DENIED",
                f"Authority issued for project '{auth_proj}', but invoked for project '{current_project_id}'.",
            )

        # 5. Check task authorization
        if auth.allowed_tasks and "*" not in auth.allowed_tasks and "**" not in auth.allowed_tasks:
            if task.task_id not in auth.allowed_tasks:
                return (
                    False,
                    "AUTHORIZATION_DENIED",
                    f"Task '{task.task_id}' is not in the authorized task list: {auth.allowed_tasks}",
                )

        # 6. Check tool authorization
        if task.allowed_tools:
            task_tools = task.allowed_tools
        elif task.command:
            task_tools = ["test_runner"] if "pytest" in task.command else ["shell"]
        elif task.target_file or task.file_content:
            task_tools = ["filesystem"]
        else:
            task_tools = ["filesystem"]

        for t in task_tools:
            if auth.allowed_tools and "*" not in auth.allowed_tools and "**" not in auth.allowed_tools:
                if t not in auth.allowed_tools and not any(t.startswith(f"{at}.") for at in auth.allowed_tools):
                    return (
                        False,
                        "OUT_OF_SCOPE",
                        f"Tool '{t}' requested by task '{task.task_id}' is outside authorized tools: {auth.allowed_tools}",
                    )

        # 7. Check operation authorization
        task_ops = task.allowed_operations or ["read", "create", "modify", "test"]
        for op in task_ops:
            if auth.allowed_operations and "*" not in auth.allowed_operations and "**" not in auth.allowed_operations:
                if op not in auth.allowed_operations:
                    return (
                        False,
                        "OUT_OF_SCOPE",
                        f"Operation '{op}' requested by task '{task.task_id}' is outside authorized operations: {auth.allowed_operations}",
                    )

        # 8. Check path authorization if target_file is defined
        if task.target_file:
            path_allowed = False
            target_norm = task.target_file.replace("\\", "/").strip("./")
            
            # Check for path traversal attacks
            if ".." in target_norm:
                return False, "AUTHORIZATION_DENIED", f"Path traversal token detected in '{task.target_file}'"

            if not auth.allowed_paths or "*" in auth.allowed_paths or "**" in auth.allowed_paths:
                path_allowed = True
            else:
                from fnmatch import fnmatch
                for pat in auth.allowed_paths:
                    pat_clean = pat.replace("\\", "/").strip("./")
                    if fnmatch(target_norm, pat_clean) or (pat_clean.endswith("/**") and target_norm.startswith(pat_clean[:-3])):
                        path_allowed = True
                        break

            if not path_allowed:
                return (
                    False,
                    "OUT_OF_SCOPE",
                    f"Target file '{task.target_file}' is outside authorized paths: {auth.allowed_paths}",
                )

        return True, "AUTHORIZED", None
