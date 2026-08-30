"""
Unit tests for VerificationPlan and TestObject definitions (Sections 7, 10, 11).
"""

from research_agents.engineering_verification.schemas import TestObject, VerificationPlan


def test_verification_plan_and_test_structure():
    plan = VerificationPlan(
        verification_plan_id="PLAN-001",
        project_id="proj_sar_001",
        requirements=["REQ-SAR-001"],
        verification_items=["SensorPower"],
        methods=["MEASUREMENT", "TEST"],
        acceptance_criteria=["3.3V ± 0.1V"],
    )
    assert plan.status == "APPROVED"
    assert "MEASUREMENT" in plan.methods

    test = TestObject(
        test_id="TEST-001",
        project_id="proj_sar_001",
        name="Power Rail Test",
        type="ELECTRICAL",
        objective="Verify rail",
        expected_results={"voltage": 3.3},
        tolerance={"voltage": 0.1},
        acceptance_criteria=["3.3V ± 0.1V"],
    )
    assert test.status == "PLANNED"
    assert test.type == "ELECTRICAL"
