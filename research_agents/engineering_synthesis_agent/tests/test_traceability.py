"""
Unit tests for TraceabilityBuilder (Section 17).
"""

from research_agents.engineering_synthesis_agent.schemas import (
    EngineeringDecision,
    EngineeringTradeoff,
    RequirementAnalysis,
    TechnicalFinding,
    ValidationRequirement,
)
from research_agents.engineering_synthesis_agent.services.traceability_builder import TraceabilityBuilder


def test_traceability_lineage_construction():
    builder = TraceabilityBuilder()

    reqs = [RequirementAnalysis(requirement_id="REQ-001", requirement="Thermal human detection", coverage="strong")]
    findings = [TechnicalFinding(finding_id="FIND-001", category="compute", finding="45 FPS on Jetson", impact_on_project="Latency margin")]
    tradeoffs = [EngineeringTradeoff(tradeoff_id="TRADE-001", decision_area="Compute", recommended_option="Jetson", reasoning="AI power")]
    decisions = [
        EngineeringDecision(
            decision_id="DEC-001",
            decision_area="Compute",
            selected_option="Jetson Orin Nano",
            decision_reason="40 TOPS compute",
            tradeoffs=["TRADE-001"],
            requirement_ids=["REQ-001"],
            evidence_ids=["ev_p_001"],
        )
    ]
    validations = [ValidationRequirement(validation_id="VAL-001", category="bench_test", description="Bench test", acceptance_criteria=">= 30 FPS", decision_ids=["DEC-001"])]

    traceability = builder.build_traceability(reqs, findings, tradeoffs, decisions, validations)

    assert len(traceability) == 1
    t = traceability[0]
    assert t.decision_id == "DEC-001"
    assert "REQ-001" in t.requirement_ids
    assert "ev_p_001" in t.evidence_ids
    assert "FIND-001" in t.finding_ids
    assert t.tradeoff_id == "TRADE-001"
    assert "VAL-001" in t.validation_ids
