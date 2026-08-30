"""
Traceability matrix generator for EngineeringComplianceAgent (Section 60).
Maps requirements -> rules -> artifacts -> evidence -> compliance results.
"""

from typing import List
from research_agents.engineering_compliance.schemas import ComplianceMatrixItem, ComplianceResult


class MatrixGenerator:
    """Generates the requirement-to-compliance traceability matrix."""

    def build_matrix(self, results: List[ComplianceResult]) -> List[ComplianceMatrixItem]:
        matrix: List[ComplianceMatrixItem] = []
        for r in results:
            ev_id = r.evidence_ids[0] if r.evidence_ids else "EVID-NONE"
            matrix.append(
                ComplianceMatrixItem(
                    requirement_id=r.requirement_id or "REQ-SAR-001",
                    rule_id=r.rule_id,
                    artifact_id=r.artifact_id,
                    evidence_id=ev_id,
                    result=r.status,
                    severity=r.severity,
                )
            )
        return matrix
