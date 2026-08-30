"""
Unit tests for Loop Guard and infinite loop prevention (Sections 41 & 42).
"""

from research_agents.project_lifecycle_orchestrator.services.next_action_engine import NextActionEngine


def test_loop_guard_halts_after_max_retries():
    engine = NextActionEngine()

    # Attempt 1 -> Continues with remediation
    a1 = engine.determine_next_action("p1", "QA", qa_status="FAILED", last_failure_type="TEST_FAILURE")
    assert a1.next_state == "PLANNING"

    # Attempt 2 -> Continues with remediation
    a2 = engine.determine_next_action("p1", "QA", qa_status="FAILED", last_failure_type="TEST_FAILURE")
    assert a2.next_state == "PLANNING"

    # Attempt 3 -> Triggers Loop Guard -> AWAITING_HUMAN
    a3 = engine.determine_next_action("p1", "QA", qa_status="FAILED", last_failure_type="TEST_FAILURE")
    assert a3.next_state == "AWAITING_HUMAN"
    assert a3.action_type == "REQUEST_HUMAN_INPUT"
    assert "Loop Guard" in a3.reason
