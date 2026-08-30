"""
Unit tests for FileVerifier service (Sections 8 & 9).
"""

from pathlib import Path
import tempfile
from research_agents.verification_qa_agent.services.file_verifier import FileVerifier


def test_file_verifier_expected_and_unauthorized_changes():
    with tempfile.TemporaryDirectory() as tmp_dir:
        verifier = FileVerifier(project_root_dir=tmp_dir)

        # Create expected file
        p = Path(tmp_dir)
        (p / "firmware" / "sensors").mkdir(parents=True, exist_ok=True)
        (p / "firmware" / "sensors" / "driver.py").write_text("# driver", encoding="utf-8")

        # Create unexpected file
        (p / "backend").mkdir(parents=True, exist_ok=True)
        (p / "backend" / "server.py").write_text("# server", encoding="utf-8")

        plan_tasks = [
            {
                "task_id": "TASK-001",
                "target_file": "firmware/sensors/driver.py",
            }
        ]

        actual_changed = [
            "firmware/sensors/driver.py",
            "backend/server.py",
        ]

        allowed_paths = ["firmware/**"]

        results = verifier.verify_changes(
            actual_changed_files=actual_changed,
            plan_tasks=plan_tasks,
            allowed_paths=allowed_paths,
        )

        assert len(results) == 2
        f_map = {r.file: r for r in results}

        assert f_map["firmware/sensors/driver.py"].status == "PASS"
        assert f_map["firmware/sensors/driver.py"].authorized is True
        assert f_map["firmware/sensors/driver.py"].expected is True

        assert f_map["backend/server.py"].status == "FAIL"
        assert f_map["backend/server.py"].authorized is False
        assert f_map["backend/server.py"].expected is False
