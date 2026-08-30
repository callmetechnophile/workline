"""
Traceability matrix generator for EngineeringVerificationAgent (Section 65).
Maps requirements -> tests -> methods -> acceptance criteria -> results -> evidence.
"""

from typing import List
from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    TestObject,
    TestResult,
    VerificationMatrixItem,
)


class VerificationMatrixGenerator:
    """Generates the requirement-to-verification traceability matrix."""

    def build_matrix(
        self,
        tests: List[TestObject],
        results: List[TestResult],
        evidence: List[EvidenceObject],
    ) -> List[VerificationMatrixItem]:
        matrix: List[VerificationMatrixItem] = []
        res_map = {r.test_id: r for r in results}
        ev_map = {ev.source: ev for ev in evidence}

        for t in tests:
            r = res_map.get(t.test_id)
            status_str = r.status if r else "NOT_EXECUTED"
            ev = ev_map.get(f"test:{t.test_id}")
            ev_id = ev.evidence_id if ev else "EVID-NONE"

            verif_status = "VERIFIED" if status_str == "PASS" else ("FAIL" if status_str == "FAIL" else "PLANNED")

            matrix.append(
                VerificationMatrixItem(
                    requirement_id="REQ-SAR-001",
                    verification_id=t.verification_id or "VERIF-001",
                    test_id=t.test_id,
                    method="TEST",
                    acceptance_criteria=t.acceptance_criteria[0] if t.acceptance_criteria else "Satisfies spec",
                    result=status_str,
                    evidence_id=ev_id,
                    version="v1.0.0",
                    status=verif_status,
                )
            )
        return matrix
