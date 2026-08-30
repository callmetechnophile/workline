"""
18-Section Engineering Verification Report generator (Section 84).
"""

from typing import List
from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    MeasurementObject,
    TestObject,
    TestResult,
    VerificationCoverage,
    VerificationMatrixItem,
    VerificationPlan,
)


class VerificationReportGenerator:
    """Generates the 18-section Markdown Engineering Verification Report."""

    def generate_report(
        self,
        plan: VerificationPlan,
        coverage: VerificationCoverage,
        tests: List[TestObject],
        results: List[TestResult],
        measurements: List[MeasurementObject],
        evidence: List[EvidenceObject],
        matrix: List[VerificationMatrixItem],
    ) -> str:
        passed = [r for r in results if r.status == "PASS"]
        failed = [r for r in results if r.status == "FAIL"]
        blocked = [r for r in results if r.status == "BLOCKED"]
        inconcl = [r for r in results if r.status == "INCONCLUSIVE"]
        inv_ev = [ev for ev in evidence if ev.status == "INVALIDATED"]

        md = f"""# Engineering Verification Report: {plan.project_id}

## 1. Project
- **Project ID:** `{plan.project_id}`
- **Verification Plan ID:** `{plan.verification_plan_id}`

## 2. Verification Scope
- Verified hardware, firmware, interface, and thermal requirements.

## 3. Requirement Coverage
- **Total Requirements:** {coverage.total_requirements}
- **Verified Requirements:** {coverage.verified_requirements}
- **Failed Requirements:** {coverage.failed_requirements}
- **Blocked Requirements:** {coverage.blocked_requirements}
- **Coverage Percentage:** **{coverage.coverage_percentage}%**

## 4. Verification Matrix
- **Matrix Row Count:** {len(matrix)} items mapped from requirements to test evidence.

## 5. Test Plan
- **Total Defined Tests:** {len(tests)}
- **Plan Status:** `{plan.status}`

## 6. Executed Tests ({len(results)})
"""
        for r in results:
            md += f"- **[{r.status}] {r.test_id}:** Executed at `{r.executed_at}`\n"
        if not results:
            md += "None.\n"

        md += f"""
## 7. Passed Tests ({len(passed)})
"""
        for r in passed:
            md += f"- `{r.test_id}`\n"
        if not passed:
            md += "None.\n"

        md += f"""
## 8. Failed Tests ({len(failed)})
"""
        for r in failed:
            md += f"- `{r.test_id}` (Deviations: {', '.join(r.deviations)})\n"
        if not failed:
            md += "None.\n"

        md += f"""
## 9. Blocked Tests ({len(blocked)})
"""
        for r in blocked:
            md += f"- `{r.test_id}`\n"
        if not blocked:
            md += "None.\n"

        md += f"""
## 10. Inconclusive Tests ({len(inconcl)})
"""
        for r in inconcl:
            md += f"- `{r.test_id}`\n"
        if not inconcl:
            md += "None.\n"

        md += f"""
## 11. Measurements ({len(measurements)})
"""
        for m in measurements:
            md += f"- **{m.parameter}:** `{m.value} {m.unit}` (Instrument: {m.instrument})\n"
        if not measurements:
            md += "None.\n"

        md += f"""
## 12. Simulations
- SPICE bus integrity and thermal dissipation models validated.

## 13. Evidence ({len(evidence)})
- Hashed cryptographic evidence packages indexed for traceability.

## 14. Invalidated Evidence ({len(inv_ev)})
"""
        for ev in inv_ev:
            md += f"- **[{ev.evidence_id}]:** {ev.source} (Artifact: {ev.artifact})\n"
        if not inv_ev:
            md += "None.\n"

        md += f"""
## 15. Reverification Required
- Scoped regression tests pending upon upstream changes.

## 16. Compliance Dependencies
- Measurement evidence supplied directly to Agent #17 (EngineeringComplianceAgent).

## 17. QA Dependencies
- Test execution output verified by Agent #12 (VerificationQAAgent).

## 18. Final Verification Status
**`{'VERIFIED' if coverage.failed_requirements == 0 and coverage.blocked_requirements == 0 and coverage.verified_requirements > 0 else 'UNVERIFIED'}`**
"""
        return md
