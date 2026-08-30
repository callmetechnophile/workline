"""
Unit tests for NextActionEngine rule evaluations (Sections 10–13).
"""

from research_agents.project_lifecycle_orchestrator.services.next_action_engine import NextActionEngine


def test_next_action_engine_qa_verified_and_failed():
    engine = NextActionEngine()

    # QA Verified -> Complete
    act_ver = engine.determine_next_action("p1", "QA", qa_status="VERIFIED")
    assert act_ver.action_type == "COMPLETE"
    assert act_ver.next_state == "VERIFIED"

    # QA Failed -> Correct Implementation
    act_fail = engine.determine_next_action(
        "p1",
        "QA",
        qa_status="FAILED",
        last_failure_type="TEST_FAILURE",
        last_failure_details="2 pytest assertions failed",
    )
    assert act_fail.action_type == "PLAN_IMPLEMENTATION"
    assert act_fail.target_agent == "ProjectExecutionAgent"
