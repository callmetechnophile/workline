"""
Unit tests for RequirementVerifier service (Sections 14 & 15).
"""

from research_agents.verification_qa_agent.schemas import (
    EvidenceObject,
    TaskVerificationObject,
    TestResultObject,
)
from research_agents.verification_qa_agent.services.requirement_verifier import RequirementVerifier


def test_requirement_verifier_traceability():
    verifier = RequirementVerifier()

    reqs = [
        {"requirement_id": "REQ-01", "description": "Thermal camera 15 FPS"},
        {"requirement_id": "REQ-02", "description": "Edge AI person detection"},
    ]

    tasks = [
        TaskVerificationObject(task_id="TASK-01", implementation_status="PASS"),
        TaskVerificationObject(task_id="TASK-02", implementation_status="PASS"),
    ]

    tests = [
        TestResultObject(test_id="TEST-01", command="pytest test_tools.py", status="PASS", passed=1),
    ]

    evidence = [
        EvidenceObject(
            evidence_id="EVID-01",
            type="test",
            source="tests/",
            result="1 passed",
            timestamp="2026-08-30T12:00:00Z",
            supports=["TEST-01"],
        )
    ]

    results = verifier.verify_requirements(
        requirements=reqs,
        task_verifications=tasks,
        test_results=tests,
        evidence_items=evidence,
    )

    assert len(results) == 2
    assert results[0].status == "PASS"
    assert results[0].coverage == "complete"
    assert "TASK-01" in results[0].implementation_tasks
