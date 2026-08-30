"""
Unit tests for BlockerEngine (Sections 17 & 18).
"""

from research_agents.project_lifecycle_orchestrator.services.blocker_engine import BlockerEngine


def test_blocker_engine_evaluations():
    engine = BlockerEngine()

    # Clean state
    b_clean = engine.evaluate_blockers("p1", {}, validation_status="READY", qa_status="VERIFIED")
    assert len(b_clean) == 0

    # Database down blocker
    b_db = engine.evaluate_blockers("p1", {}, db_healthy=False)
    assert any(b.type == "DATABASE_UNAVAILABLE" for b in b_db)

    # Auth denied blocker
    b_auth = engine.evaluate_blockers("p1", {}, auth_granted=False)
    assert any(b.type == "AUTHORIZATION_DENIED" for b in b_auth)

    # QA failure blocker
    b_qa = engine.evaluate_blockers("p1", {}, qa_status="FAILED")
    assert any(b.type == "QA_GATE_FAILURE" for b in b_qa)
