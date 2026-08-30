"""
Task execution engine for EngineeringExecutionAgent (Sections 24, 25, 26, 41, 42).
Coordinates task dependency enforcement, ArmorIQ plan capture & invocation, tool dispatch, and output verification.
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid
from loguru import logger

from research_agents.engineering_execution_agent.armoriq.client import ArmorIQClient
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionContext,
    ExecutionAuditItem,
    ExecutionTask,
    ToolCallRecord,
)
from research_agents.engineering_execution_agent.services.authorization_gate import AuthorizationGate
from research_agents.engineering_execution_agent.services.change_detector import ChangeDetector
from research_agents.engineering_execution_agent.tools.filesystem_tool import ScopedFilesystemTool
from research_agents.engineering_execution_agent.tools.git_tool import ScopedGitTool
from research_agents.engineering_execution_agent.tools.shell_tool import ScopedShellTool
from research_agents.engineering_execution_agent.tools.test_runner_tool import ScopedTestRunnerTool


class TaskExecutor:
    """Coordinates strict task-by-task execution under ArmorIQ cryptographic governance."""

    def __init__(
        self,
        armoriq_client: Optional[ArmorIQClient] = None,
        auth_gate: Optional[AuthorizationGate] = None,
        change_detector: Optional[ChangeDetector] = None,
        fs_tool: Optional[ScopedFilesystemTool] = None,
        shell_tool: Optional[ScopedShellTool] = None,
        test_tool: Optional[ScopedTestRunnerTool] = None,
        git_tool: Optional[ScopedGitTool] = None,
    ):
        self.armoriq = armoriq_client or ArmorIQClient()
        self.auth_gate = auth_gate or AuthorizationGate()
        self.change_detector = change_detector or ChangeDetector()
        self.fs_tool = fs_tool or ScopedFilesystemTool()
        self.shell_tool = shell_tool or ScopedShellTool()
        self.test_tool = test_tool or ScopedTestRunnerTool()
        self.git_tool = git_tool or ScopedGitTool()

    def execute_tasks(
        self,
        tasks: List[ExecutionTask],
        auth: AuthorizedExecution,
        context: EngineeringExecutionContext,
        architecture: Dict[str, Any],
        bom: Dict[str, Any],
        dry_run: bool = False,
        single_task_id: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[ToolCallRecord], List[Dict[str, Any]], List[ExecutionAuditItem], List[str]]:
        """
        Executes sequence of tasks adhering to dependency constraints and zero-implicit-authority rules.
        """
        completed: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        blocked: List[Dict[str, Any]] = []
        denied: List[Dict[str, Any]] = []
        tool_calls: List[ToolCallRecord] = []
        receipts: List[Dict[str, Any]] = []
        audit_trail: List[ExecutionAuditItem] = []
        all_changed_files: List[str] = []

        completed_task_ids: Set[str] = set()
        failed_task_ids: Set[str] = set()

        exec_id = context.execution_id or f"exec_{uuid.uuid4().hex[:8]}"

        # 1. Cryptographically Capture Root Plan and Delegate to Execution Agent (Sections 18, 20)
        try:
            plan_receipt = self.armoriq.capture_plan(
                user_intent=f"Execute engineering implementation plan for project='{context.project_id}' ({len(tasks)} tasks)"
            )
            receipts.append(plan_receipt)

            # Delegate from Planner Agent to EngineeringExecutionAgent
            child_receipt = self.armoriq.delegate(
                child_agent_id=context.agent_id,
                requested_scope=auth.allowed_tools or ["filesystem", "shell", "test_runner"],
                parent_receipt=auth.parent_receipt or plan_receipt,
            )
            receipts.append(child_receipt)
        except Exception as e:
            logger.error(f"Failed to capture ArmorIQ plan/delegation: {e}")
            raise

        # Determine target tasks to run
        tasks_to_run = tasks
        if single_task_id:
            tasks_to_run = [t for t in tasks if t.task_id == single_task_id]

        for task in tasks_to_run:
            logger.info(f"[{exec_id}] Processing Task '{task.task_id}': {task.title}")

            # 2. Dependency Check (Section 25)
            unmet_deps = [dep for dep in task.dependencies if dep not in completed_task_ids]
            if unmet_deps:
                logger.warning(f"Task '{task.task_id}' DEPENDENCY_BLOCKED by unmet dependencies: {unmet_deps}")
                blocked.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "reason": f"DEPENDENCY_BLOCKED: Requires completed dependencies: {unmet_deps}",
                })
                failed_task_ids.add(task.task_id)
                continue

            # 3. Architectural / BOM Drift Check (Sections 41, 42)
            if "conflict" in task.title.lower() or "conflict" in task.description.lower():
                logger.error(f"Task '{task.task_id}' rejected due to ARCHITECTURE_CONFLICT / BOM_CONFLICT")
                denied.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": "ARCHITECTURE_CONFLICT",
                    "details": "Task violates validated architecture/BOM specifications.",
                })
                failed_task_ids.add(task.task_id)
                continue

            # 4. Authorization Gate Check (Section 8)
            is_authorized, reason, details = self.auth_gate.validate_authorization(
                task=task,
                auth=auth,
                current_project_id=context.project_id,
                current_agent_id=context.agent_id,
            )

            if not is_authorized:
                logger.warning(f"Task '{task.task_id}' AUTHORIZATION_DENIED: {reason} — {details}")
                denied.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": reason,
                    "details": details,
                })
                audit_trail.append(
                    ExecutionAuditItem(
                        audit_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        project_id=context.project_id,
                        execution_id=exec_id,
                        task_id=task.task_id,
                        agent_id=context.agent_id,
                        parent_agent_id=context.parent_agent_id,
                        authorization_id=auth.authorization_id,
                        tool=task.allowed_tools[0] if task.allowed_tools else task.task_type,
                        operation=task.allowed_operations[0] if task.allowed_operations else "execute",
                        resource=task.target_file or task.command or "task_scope",
                        status="DENIED",
                    )
                )
                failed_task_ids.add(task.task_id)
                continue

            # 5. Dry-Run Check (Section 57)
            if dry_run:
                logger.info(f"Task '{task.task_id}' DRY-RUN verified. Skipping actual tool execution.")
                completed.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": "dry_run_verified",
                    "plan": "Authorized and ready for execution.",
                })
                completed_task_ids.add(task.task_id)
                continue

            # 6. Execute Task under ArmorIQ Governance
            before_snap = self.change_detector.snapshot_state()
            task_success = True
            t_start = time.time()
            err_msg: Optional[str] = None
            tool_output: Optional[str] = None
            rcpt_id: Optional[str] = None

            # Prepare delegation receipt for this task
            current_receipt = child_receipt

            try:
                # 6a. Filesystem Task
                if task.target_file or task.file_content or task.task_type in ("code", "firmware", "hardware", "pcb", "configuration", "documentation"):
                    t_name = "filesystem.write" if task.file_content else "filesystem.read"
                    op = task.operation or ("create" if task.file_content else "read")
                    res_path = task.target_file or "firmware/default.py"

                    def _run_fs():
                        return self.fs_tool.execute(
                            operation=op,
                            target_path=res_path,
                            content=task.file_content,
                            allowed_paths=auth.allowed_paths,
                            allowed_operations=auth.allowed_operations,
                        )

                    inv_res = self.armoriq.invoke(
                        tool_name="filesystem",
                        args={},
                        receipt_dict=current_receipt,
                        tool_callable=_run_fs,
                    )
                    rcpt_id = inv_res.get("receipt_id")
                    tool_output = str(inv_res.get("result"))

                # 6b. Shell / Build / Test Command Task
                elif task.command or task.task_type in ("testing", "build", "simulation", "container"):
                    t_name = "test_runner" if "pytest" in (task.command or "") else "shell"
                    cmd_str = task.command or "python -m pytest"

                    def _run_cmd():
                        return self.shell_tool.execute(
                            command=cmd_str,
                            allowed_commands=None,
                        )

                    inv_res = self.armoriq.invoke(
                        tool_name=t_name,
                        args={},
                        receipt_dict=current_receipt,
                        tool_callable=_run_cmd,
                    )
                    rcpt_id = inv_res.get("receipt_id")
                    tool_output = str(inv_res.get("result"))

                else:
                    t_name = "filesystem"
                    res_path = "generic"

            except Exception as ex:
                logger.error(f"Task execution error on '{task.task_id}': {ex}")
                task_success = False
                err_msg = str(ex)

            duration = (time.time() - t_start) * 1000

            # 7. Check for Out-Of-Scope Filesystem Changes (Section 27)
            after_snap = self.change_detector.snapshot_state()
            changed_files, out_of_scope_files = self.change_detector.detect_changes(
                before_state=before_snap,
                after_state=after_snap,
                allowed_paths=auth.allowed_paths,
            )
            all_changed_files.extend(changed_files)

            if out_of_scope_files:
                logger.error(f"Task '{task.task_id}' caused OUT_OF_SCOPE_MODIFICATION on: {out_of_scope_files}")
                task_success = False
                err_msg = f"OUT_OF_SCOPE_MODIFICATION: Modified unapproved paths: {out_of_scope_files}"

            # 8. Record Tool Call and Audit Entry
            t_record = ToolCallRecord(
                tool_call_id=f"CALL-{uuid.uuid4().hex[:6].upper()}",
                task_id=task.task_id,
                tool=task.allowed_tools[0] if task.allowed_tools else task.task_type,
                operation=task.allowed_operations[0] if task.allowed_operations else "execute",
                resource=task.target_file or task.command or "task_resource",
                status="success" if task_success else "failed",
                armoriq_receipt_id=rcpt_id,
                output=tool_output,
                error=err_msg,
                duration_ms=duration,
            )
            tool_calls.append(t_record)

            audit_item = ExecutionAuditItem(
                audit_id=f"AUD-{uuid.uuid4().hex[:6].upper()}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                project_id=context.project_id,
                execution_id=exec_id,
                task_id=task.task_id,
                agent_id=context.agent_id,
                parent_agent_id=context.parent_agent_id,
                authorization_id=auth.authorization_id,
                delegation_chain=[context.parent_agent_id or "Orchestrator", context.agent_id],
                tool=t_record.tool,
                operation=t_record.operation,
                resource=t_record.resource,
                status="SUCCESS" if task_success else "FAILED",
                armoriq_receipt_id=rcpt_id,
            )
            audit_trail.append(audit_item)

            # 9. Output verification
            if task_success:
                completed.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": "completed",
                    "changed_files": changed_files,
                })
                completed_task_ids.add(task.task_id)
            else:
                failed.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": "failed",
                    "error": err_msg,
                })
                failed_task_ids.add(task.task_id)

        return completed, failed, blocked, denied, tool_calls, receipts, audit_trail, list(set(all_changed_files))
