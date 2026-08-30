"""
Verification and requirement coverage calculator (Sections 66 & 67).
"""

from typing import List
from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    TestObject,
    TestResult,
    VerificationCoverage,
    VerificationPlan,
)


class CoverageCalculator:
    """Calculates requirement, test, and verification evidence coverage."""

    def compute_coverage(
        self,
        project_id: str,
        plan: VerificationPlan,
        tests: List[TestObject],
        results: List[TestResult],
        evidence: List[EvidenceObject],
    ) -> VerificationCoverage:
        total_reqs = len(plan.requirements) or 1
        passed_tests = sum(1 for r in results if r.status == "PASS")
        failed_tests = sum(1 for r in results if r.status == "FAIL")
        blocked_tests = sum(1 for r in results if r.status == "BLOCKED")
        unexec_tests = sum(1 for r in results if r.status in ("PLANNED", "NOT_EXECUTED"))

        verified_reqs = min(passed_tests, total_reqs) if failed_tests == 0 and blocked_tests == 0 else 0
        failed_reqs = min(failed_tests, total_reqs)
        blocked_reqs = min(blocked_tests, total_reqs)
        pending_reqs = max(0, total_reqs - verified_reqs - failed_reqs - blocked_reqs)

        pct = (verified_reqs / total_reqs) * 100.0 if total_reqs > 0 else 0.0

        return VerificationCoverage(
            project_id=project_id,
            total_requirements=total_reqs,
            verified_requirements=verified_reqs,
            failed_requirements=failed_reqs,
            blocked_requirements=blocked_reqs,
            pending_requirements=pending_reqs,
            total_tests=len(tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            blocked_tests=blocked_tests,
            unexecuted_tests=unexec_tests,
            total_evidence=len(evidence),
            coverage_percentage=round(pct, 1),
        )
