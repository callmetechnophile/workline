"""
Unit tests for unexecuted tests and blocked hardware dependencies (Sections 78, 101, 104).
"""

from research_agents.engineering_verification.schemas import TestObject
from research_agents.engineering_verification.services.test_executor import VerificationExecutor


def test_unexecuted_and_blocked_states():
    executor = VerificationExecutor()

    test = TestObject(
        test_id="TEST-001",
        project_id="proj_sar_001",
        name="Power Rail",
        type="ELECTRICAL",
        objective="Rail",
        expected_results={"voltage": 3.3},
    )

    # 1. Unexecuted test -> NOT_EXECUTED (never PASS, Section 101)
    res_unexec, _, _ = executor.execute_test(test, actual_data=None)
    assert res_unexec.status == "NOT_EXECUTED"

    # 2. Missing hardware fixture -> BLOCKED (never PASS, Section 104)
    res_blocked, _, _ = executor.execute_test(test, actual_data={"voltage": 3.3}, hardware_available=False)
    assert res_blocked.status == "BLOCKED"
