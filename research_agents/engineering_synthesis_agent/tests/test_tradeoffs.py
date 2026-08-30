"""
Unit tests for TradeoffAnalyzer and DecisionEngine.
"""

from research_agents.engineering_synthesis_agent.schemas import ProjectMeta
from research_agents.engineering_synthesis_agent.services.decision_engine import DecisionEngine
from research_agents.engineering_synthesis_agent.services.finding_extractor import FindingExtractor
from research_agents.engineering_synthesis_agent.services.requirement_mapper import RequirementMapper
from research_agents.engineering_synthesis_agent.services.tradeoff_analyzer import TradeoffAnalyzer


def test_tradeoff_analysis_and_decision_generation():
    analyzer = TradeoffAnalyzer()
    decision_engine = DecisionEngine()
    req_mapper = RequirementMapper()
    finding_extractor = FindingExtractor()

    project = ProjectMeta(
        title="SAR Drone",
        requirements=["Real-time human detection"],
    )

    deep_research = {
        "component_trade_studies": [
            {
                "component_type": "Edge Compute",
                "candidates_evaluated": ["Jetson Orin Nano", "Raspberry Pi 5"],
                "tradeoff_matrix": {"Jetson Orin Nano": {"TOPS": 40}, "Raspberry Pi 5": {"TOPS": 0}},
                "recommended_option": "Jetson Orin Nano",
                "recommendation_reason": "Real-time AI acceleration capability.",
            }
        ]
    }

    tradeoffs = analyzer.analyze_tradeoffs(project, deep_research, evidence_items=[])
    assert len(tradeoffs) >= 1
    assert tradeoffs[0].recommended_option == "Jetson Orin Nano"
    assert len(tradeoffs[0].options) == 2

    findings = finding_extractor.extract_findings(deep_research, [], [])
    reqs = req_mapper.map_requirements(project, [], [f.finding_id for f in findings])

    decisions, recs, assumptions, unknowns = decision_engine.generate_decisions_and_recommendations(
        project, reqs, findings, tradeoffs
    )

    assert len(decisions) >= 1
    assert decisions[0].selected_option == "Jetson Orin Nano"
    assert "REQ-001" in decisions[0].requirement_ids
    assert decisions[0].validation_required is True

    assert len(recs) >= 1
    assert len(assumptions) >= 1
    assert len(unknowns) >= 1
