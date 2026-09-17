"""Tests for recovery and rollback planning."""
from research_agents.deployment_operations.services.recovery_rollback_engine import RecoveryRollbackEngine


def test_recovery_and_rollback():
    engine = RecoveryRollbackEngine()
    actions = engine.build_recovery_plans("SYS-1")
    assert len(actions) >= 2
    assert any(a.strategy == "RESTART" for a in actions)
    assert any(a.strategy == "DEGRADED" for a in actions)

    rollback = engine.build_rollback_plan("SYS-1")
    assert rollback.current_version == "1.1.0"
    assert rollback.target_version == "1.0.0"
    assert rollback.is_destructive is False

    backup = engine.build_backup_restore_plan("SYS-1")
    assert "SurrealDB" in backup.backup_target
