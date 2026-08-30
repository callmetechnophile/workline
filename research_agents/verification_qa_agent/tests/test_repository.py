"""
Unit tests for VerificationRepository interface (Section 71).
"""

import pytest
from research_agents.verification_qa_agent.repository import InMemoryVerificationRepository
from research_agents.verification_qa_agent.schemas import (
    CorrectionReportItem,
    EvidenceObject,
    FinalQAVerdict,
    RequirementVerificationItem,
    TestResultObject,
    VerificationQAAgentOutput,
    VerificationTraceabilityItem,
)


@pytest.mark.asyncio
async def test_verification_repository_all_methods():
    repo = InMemoryVerificationRepository()
    v_id = "QA-TEST-001"

    # Save test result
    await repo.save_test_result(
        TestResultObject(test_id="TEST-01", command="pytest", status="PASS"),
        v_id,
    )

    # Save requirement result
    await repo.save_requirement_result(
        RequirementVerificationItem(requirement_id="REQ-01", status="PASS"),
        v_id,
    )

    # Save failure
    await repo.save_failure(
        CorrectionReportItem(
            correction_id="CORR-01",
            failure_id="FAIL-01",
            problem="Missing test",
            recommended_correction="Add test",
        ),
        v_id,
    )

    # Save evidence
    await repo.save_evidence(
        EvidenceObject(
            evidence_id="EVID-01",
            type="test",
            source="tests/",
            result="Passed",
            timestamp="2026-08-30",
        ),
        v_id,
    )

    # Save traceability
    await repo.save_traceability(
        VerificationTraceabilityItem(traceability_id="TRACE-01", requirement_ids=["REQ-01"]),
        v_id,
    )

    # Save QA verdict
    fv = FinalQAVerdict(verdict="VERIFIED")
    await repo.save_qa_verdict(fv, v_id)

    # Save complete verification
    output = VerificationQAAgentOutput(
        status="success",
        verification_id=v_id,
        project_id="proj_01",
        verdict="VERIFIED",
        final_verdict=fv,
    )
    saved_id = await repo.save_verification(output)
    assert saved_id == v_id

    retrieved = await repo.get_verification(v_id)
    assert retrieved is not None
    assert retrieved.verdict == "VERIFIED"
