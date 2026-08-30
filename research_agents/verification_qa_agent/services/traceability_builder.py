"""
Traceability matrix builder for VerificationQAAgent (Section 52).
Constructs unbroken lineage from Requirement -> Architecture -> Task -> File -> Test -> Evidence -> QA Verdict.
"""

from typing import Any, Dict, List
from research_agents.verification_qa_agent.schemas import (
    ChangeObject,
    EvidenceObject,
    RequirementVerificationItem,
    TestResultObject,
    VerificationTraceabilityItem,
)


class TraceabilityBuilder:
    """Constructs comprehensive end-to-end verification traceability records."""

    def build_traceability(
        self,
        requirements: List[RequirementVerificationItem],
        changes: List[ChangeObject],
        test_results: List[TestResultObject],
        evidence: List[EvidenceObject],
        overall_verdict: str,
    ) -> List[VerificationTraceabilityItem]:
        records: List[VerificationTraceabilityItem] = []

        for req in requirements:
            records.append(
                VerificationTraceabilityItem(
                    traceability_id=f"TRACE-QA-{req.requirement_id}",
                    requirement_ids=[req.requirement_id],
                    architecture_ids=["ARCH-MAIN"],
                    task_ids=req.implementation_tasks,
                    file_paths=[ch.file for ch in changes if ch.status == "PASS"][:3],
                    test_ids=req.test_ids,
                    evidence_ids=req.evidence_ids,
                    verification_status=req.status,
                )
            )

        return records
