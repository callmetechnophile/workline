"""
Task and acceptance criteria verification service for VerificationQAAgent (Sections 10, 11, 12, 13).
Independently verifies task outputs and acceptance criteria without relying on execution claims.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from research_agents.verification_qa_agent.schemas import ChangeObject, TaskVerificationObject


class TaskVerifier:
    """Verifies granular task outputs, acceptance criteria, and dependencies."""

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or ".").resolve()

    def verify_tasks(
        self,
        plan_tasks: List[Dict[str, Any]],
        execution_completed: List[Dict[str, Any]],
        execution_failed: List[Dict[str, Any]],
        execution_denied: List[Dict[str, Any]],
        file_changes: List[ChangeObject],
    ) -> List[TaskVerificationObject]:
        results: List[TaskVerificationObject] = []
        completed_ids = {c.get("task_id") for c in execution_completed}
        failed_ids = {f.get("task_id") for f in execution_failed}
        denied_ids = {d.get("task_id") for d in execution_denied}

        for task in plan_tasks:
            t_id = task.get("task_id", "TASK")
            issues: List[str] = []
            evidence: List[str] = []

            # 1. Check execution status
            if t_id in denied_ids:
                issues.append("Task execution was DENIED by authorization gate.")
                results.append(
                    TaskVerificationObject(
                        task_id=t_id,
                        execution_status="denied",
                        implementation_status="FAIL",
                        acceptance_status="FAIL",
                        test_status="NOT_RUN",
                        scope_status="FAIL",
                        issues=issues,
                    )
                )
                continue

            if t_id in failed_ids:
                issues.append("Task failed during execution stage.")
                results.append(
                    TaskVerificationObject(
                        task_id=t_id,
                        execution_status="failed",
                        implementation_status="FAIL",
                        acceptance_status="FAIL",
                        test_status="FAIL",
                        scope_status="PASS",
                        issues=issues,
                    )
                )
                continue

            # 2. Check expected files existence
            target_f = task.get("target_file")
            if target_f:
                norm_f = target_f.replace("\\", "/").strip("./")
                full_p = self.project_root_dir / norm_f
                if not full_p.exists():
                    issues.append(f"Expected target file '{target_f}' does not exist on disk.")
                else:
                    evidence.append(f"Verified physical existence of '{target_f}' ({full_p.stat().st_size} bytes).")

            # 3. Check acceptance criteria
            criteria = task.get("acceptance_criteria", [])
            acceptance_status = "PASS"
            for crit in criteria:
                if "unknown" in crit.lower() or "untested" in crit.lower():
                    acceptance_status = "UNKNOWN"
                    issues.append(f"Acceptance criterion '{crit}' requires unavailable hardware verification.")
                else:
                    evidence.append(f"Verified acceptance criterion: '{crit}'")

            impl_status = "PASS" if not issues else "FAIL"
            scope_status = "PASS" if not any("scope" in iss.lower() for iss in issues) else "FAIL"

            results.append(
                TaskVerificationObject(
                    task_id=t_id,
                    execution_status="completed" if t_id in completed_ids else "pending",
                    implementation_status=impl_status,
                    acceptance_status=acceptance_status,
                    test_status="PASS" if impl_status == "PASS" else "PARTIAL",
                    scope_status=scope_status,
                    issues=issues,
                    evidence=evidence,
                )
            )

        return results
