"""
Unit tests for RiskAnalyzer and ValidationPlanner services.
"""

from research_agents.engineering_synthesis_agent.schemas import (
    EngineeringDecision,
    ProjectMeta,
)
from research_agents.engineering_synthesis_agent.services.risk_analyzer import RiskAnalyzer
from research_agents.engineering_synthesis_agent.services.validation_planner import ValidationPlanner


def test_risks_and_validation_planning():
    risk_analyzer = RiskAnalyzer()
    validation_planner = ValidationPlanner()

    project = ProjectMeta(title="SAR Drone")
    decisions = [
        EngineeringDecision(
            decision_id="DEC-001",
            decision_area="Compute Module",
            selected_option="Jetson Orin Nano",
            decision_reason="40 TOPS compute",
            confidence=0.95,
        )
    ]

    risks = risk_analyzer.analyze_risks(project, decisions)
    assert len(risks) >= 2
    categories = {r.category for r in risks}
    assert "thermal" in categories
    assert "power" in categories

    validations, experiments = validation_planner.plan_validation(project, decisions)
    assert len(validations) >= 1
    assert any("DEC-001" in v.decision_ids for v in validations)

    assert len(experiments) >= 1
    assert "EXP-001" in experiments[0].experiment_id
    assert len(experiments[0].acceptance_criteria) >= 1
