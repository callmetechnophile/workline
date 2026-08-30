"""
Unit tests for deterministic project completion and health checks (Sections 56–59).
"""

from research_agents.project_lifecycle_orchestrator.schemas import BlockerObject
from research_agents.project_lifecycle_orchestrator.services.health_service import ProjectHealthService


def test_completion_and_health_checks():
    service = ProjectHealthService()

    # 1. Project is complete when QA is verified and validation is ready
    assert service.is_project_complete("QA", "VERIFIED", "READY", []) is True

    # 2. Incomplete if QA failed
    assert service.is_project_complete("QA", "FAILED", "READY", []) is False

    # 3. Incomplete if blockers exist
    blk = BlockerObject(
        blocker_id="B1",
        type="VALIDATION_FAILURE",
        severity="critical",
        source="Val",
        affected_project="p1",
        resolution="Fix",
    )
    assert service.is_project_complete("QA", "VERIFIED", "READY", [blk]) is False

    # 4. Health evaluation
    health = service.get_project_health("p1", "QA", qa_status="VERIFIED", validation_status="READY")
    assert health.health == "healthy"
