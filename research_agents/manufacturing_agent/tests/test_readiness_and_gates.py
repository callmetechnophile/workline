"""Tests for Manufacturing Readiness Gates (Section 41)."""
from research_agents.manufacturing_agent.schemas import DFAModel, DFMFinding
from research_agents.manufacturing_agent.services.readiness_evaluator import ReadinessEvaluator

def test_readiness_blocker_detection():
    evaluator = ReadinessEvaluator()
    findings = [
        DFMFinding(
            finding_id="DFM-01",
            component_id="BASE",
            category="MATERIAL_PROCESS_MISMATCH",
            severity="BLOCKER",
            description="Cast Iron bending impossible",
        )
    ]
    readiness = evaluator.evaluate_readiness("P-01", findings, [], [], [])
    assert readiness.verdict == "DFM_BLOCKED"
    assert len(readiness.active_blockers) == 1

def test_prototype_ready_verdict():
    evaluator = ReadinessEvaluator()
    readiness = evaluator.evaluate_readiness("P-02", [], [], [], [])
    assert readiness.verdict == "PROTOTYPE_READY"
    assert readiness.composite_manufacturability_score >= 80.0
