"""
Unit tests for HumanDecisionManager (Sections 23–25, 66).
"""

from research_agents.project_lifecycle_orchestrator.services.human_manager import HumanDecisionManager


def test_human_decision_workflow():
    manager = HumanDecisionManager()

    # Create approval request
    req = manager.create_human_request(
        project_id="p1",
        reason="Material architecture change to SPI bus",
        requested_decision="Approve redesign to 15 FPS VoSPI",
    )
    assert req.status == "pending"

    # Pending list check
    pending = manager.get_pending_requests("p1")
    assert len(pending) == 1

    # Approve request
    appr = manager.approve_request(req.request_id, "user_001")
    assert appr.status == "approved"
    assert len(manager.get_pending_requests("p1")) == 0
