"""
Unit tests for deterministic test oracle and tolerance evaluation (Sections 28, 76, 102, 103).
"""

from research_agents.engineering_verification.schemas import TestObject
from research_agents.engineering_verification.services.test_executor import VerificationExecutor


def test_test_execution_pass_and_fail():
    executor = VerificationExecutor()

    test = TestObject(
        test_id="TEST-VOLT-01",
        project_id="proj_sar_001",
        name="Rail Voltage",
        type="ELECTRICAL",
        objective="Verify 3.3V rail",
        expected_results={"voltage": 3.3},
        tolerance={"voltage": 0.1},
        acceptance_criteria=["3.3V ± 0.1V"],
    )

    # 1. Measured 3.28V -> PASS (Section 102)
    res_pass, meas_pass, ev_pass = executor.execute_test(test, {"voltage": 3.28})
    assert res_pass.status == "PASS"
    assert meas_pass is not None
    assert meas_pass.value == 3.28
    assert ev_pass.hash is not None

    # 2. Measured 3.7V -> FAIL (Section 103)
    res_fail, meas_fail, ev_fail = executor.execute_test(test, {"voltage": 3.7})
    assert res_fail.status == "FAIL"
    assert len(res_fail.deviations) > 0
