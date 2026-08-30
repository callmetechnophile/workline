"""
Unit tests for ChangeDetector (Sections 27, 77).
"""

from pathlib import Path
import tempfile
from research_agents.engineering_execution_agent.services.change_detector import ChangeDetector


def test_change_detector_detects_in_scope_and_out_of_scope_changes():
    with tempfile.TemporaryDirectory() as tmp_dir:
        detector = ChangeDetector(project_root_dir=tmp_dir)

        # 1. Initial snapshot
        before_snap = detector.snapshot_state()

        # 2. Make an authorized file change and an unauthorized file change
        dir_p = Path(tmp_dir)
        (dir_p / "firmware" / "sensors").mkdir(parents=True, exist_ok=True)
        (dir_p / "firmware" / "sensors" / "driver.py").write_text("# sensor", encoding="utf-8")

        (dir_p / "backend").mkdir(parents=True, exist_ok=True)
        (dir_p / "backend" / "server.py").write_text("# server", encoding="utf-8")

        # 3. After snapshot
        after_snap = detector.snapshot_state()

        # 4. Compare with allowed_paths=["firmware/**"]
        changed, out_of_scope = detector.detect_changes(
            before_state=before_snap,
            after_state=after_snap,
            allowed_paths=["firmware/**"],
        )

        assert len(changed) == 2
        assert "backend/server.py" in out_of_scope
        assert "firmware/sensors/driver.py" not in out_of_scope
