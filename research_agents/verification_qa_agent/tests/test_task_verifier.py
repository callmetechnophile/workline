"""
Unit tests for TaskVerifier service (Sections 10 & 11).
"""

from pathlib import Path
import tempfile
from research_agents.verification_qa_agent.services.task_verifier import TaskVerifier


def test_task_verifier_success_and_denied_scenarios():
    with tempfile.TemporaryDirectory() as tmp_dir:
        verifier = TaskVerifier(project_root_dir=tmp_dir)

        # Create target file for task 1
        p = Path(tmp_dir)
        (p / "firmware").mkdir(parents=True, exist_ok=True)
        (p / "firmware" / "driver.py").write_text("# driver code", encoding="utf-8")

        plan_tasks = [
            {
                "task_id": "TASK-001",
                "target_file": "firmware/driver.py",
                "acceptance_criteria": ["Driver returns valid readings"],
            },
            {
                "task_id": "TASK-002",
                "target_file": "hardware/untested.py",
                "acceptance_criteria": ["Untested physical actuator response"],
            },
        ]

        completed = [{"task_id": "TASK-001"}]
        failed = []
        denied = [{"task_id": "TASK-002"}]

        results = verifier.verify_tasks(
            plan_tasks=plan_tasks,
            execution_completed=completed,
            execution_failed=failed,
            execution_denied=denied,
            file_changes=[],
        )

        assert len(results) == 2
        t1 = next(t for t in results if t.task_id == "TASK-001")
        t2 = next(t for t in results if t.task_id == "TASK-002")

        assert t1.implementation_status == "PASS"
        assert t1.acceptance_status == "PASS"

        assert t2.execution_status == "denied"
        assert t2.implementation_status == "FAIL"
