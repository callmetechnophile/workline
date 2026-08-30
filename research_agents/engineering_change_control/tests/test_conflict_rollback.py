"""
Unit tests for ConflictDetector and RollbackManager (Sections 65–71).
"""

from research_agents.engineering_change_control.schemas import ChangeRequest
from research_agents.engineering_change_control.services.conflict_detector import ConflictDetector
from research_agents.engineering_change_control.services.rollback_manager import RollbackManager


def test_conflict_detection_and_history_preserving_rollback():
    # 1. Conflict Detection
    detector = ConflictDetector()
    chg1 = ChangeRequest(
        change_id="C1",
        project_id="p1",
        change_type="COMPONENT_CHANGE",
        title="Replace MCU",
        description="Upgrade to ESP32",
        target_artifact="COMP-MCU-01",
        status="ANALYZING",
    )
    chg2 = ChangeRequest(
        change_id="C2",
        project_id="p1",
        change_type="COMPONENT_CHANGE",
        title="Replace MCU with RP2040",
        description="Upgrade to RP2040",
        target_artifact="COMP-MCU-01",
        status="ANALYZING",
    )

    conf = detector.detect_conflicts([chg1], chg2)
    assert conf is not None
    assert conf.artifact == "COMP-MCU-01"

    # 2. History-Preserving Forward Rollback
    rollback_mgr = RollbackManager()
    rollback, new_ver = rollback_mgr.execute_rollback(
        artifact_id="ARCH-001",
        target_version="v1.0.0",
        current_version="v2.0.0",
        approved_by="lead_bob",
    )
    assert rollback.target_version == "v1.0.0"
    assert new_ver.version == "v3.0.0"
    assert new_ver.supersedes == "v2.0.0"
