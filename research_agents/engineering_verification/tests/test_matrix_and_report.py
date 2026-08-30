"""
Unit tests for VerificationMatrixGenerator and VerificationReportGenerator (Sections 65 & 84).
"""

from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    TestObject,
    TestResult,
    VerificationCoverage,
    VerificationPlan,
)
from research_agents.engineering_verification.services.matrix_generator import VerificationMatrixGenerator
from research_agents.engineering_verification.services.report_generator import VerificationReportGenerator


def test_matrix_and_18_section_report():
    matrix_gen = VerificationMatrixGenerator()
    report_gen = VerificationReportGenerator()

    t = TestObject(
        test_id="T1",
        project_id="p1",
        name="Test 1",
        objective="Obj",
    )
    r = TestResult(
        test_result_id="TR1",
        test_id="T1",
        status="PASS",
    )
    ev = EvidenceObject(
        evidence_id="E1",
        type="TEST_RESULT",
        source="test:T1",
        artifact="sensor",
    )

    matrix = matrix_gen.build_matrix([t], [r], [ev])
    assert len(matrix) == 1
    assert matrix[0].status == "VERIFIED"

    plan = VerificationPlan(
        verification_plan_id="PLAN-1",
        project_id="p1",
        requirements=["REQ-1"],
    )
    cov = VerificationCoverage(
        project_id="p1",
        total_requirements=1,
        verified_requirements=1,
        coverage_percentage=100.0,
    )

    report_md = report_gen.generate_report(
        plan=plan,
        coverage=cov,
        tests=[t],
        results=[r],
        measurements=[],
        evidence=[ev],
        matrix=matrix,
    )

    assert "# Engineering Verification Report" in report_md
    assert "## 18. Final Verification Status" in report_md
    assert "VERIFIED" in report_md
