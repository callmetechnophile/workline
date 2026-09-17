"""Tests for change control cost impact evaluation."""
from research_agents.cost_supply_chain.services.change_cost_engine import ChangeCostEngine


def test_change_cost_savings():
    engine = ChangeCostEngine()
    # Recurring saves $3/unit, tooling costs $1000 -> At 1000 units: (-3*1000) + 1000 = -$2000
    impact = engine.evaluate_change_cost("ECR-1", "PROJ-1", "Material Change", -3.0, 1000.0, annualized_volume=1000)
    assert impact.annual_cost_impact == -2000.0
    assert impact.recommendation == "APPROVE"


def test_change_cost_increase():
    engine = ChangeCostEngine()
    impact = engine.evaluate_change_cost("ECR-2", "PROJ-1", "Ruggedization", 5.0, 2000.0, annualized_volume=1000)
    assert impact.annual_cost_impact == 7000.0
    assert impact.recommendation == "REVIEW_REQUIRED"
