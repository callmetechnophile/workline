"""Tests for supply chain risk assessment engine."""
from research_agents.cost_supply_chain.schemas import LifecycleStatus, PartCost, RiskType
from research_agents.cost_supply_chain.services.supply_risk_engine import SupplyRiskEngine


def test_assess_risks():
    engine = SupplyRiskEngine()
    parts = [
        PartCost(
            part_id="P1",
            part_name="Sole Source ASIC",
            unit_cost=80.0,
            is_single_source=True,
            lead_time_weeks=28.0,
            lifecycle_status=LifecycleStatus.NRND,
            moq=5000,
        ),
        PartCost(
            part_id="P2",
            part_name="Standard Resistor",
            unit_cost=0.01,
            is_single_source=False,
            lead_time_weeks=4.0,
            lifecycle_status=LifecycleStatus.ACTIVE,
            moq=100,
        ),
    ]
    risks = engine.assess_bom_risks("PROJ-RISK", parts, target_volume=1000)
    risk_types = [r.risk_type for r in risks]
    assert RiskType.SINGLE_SOURCE in risk_types
    assert RiskType.OBSOLESCENCE in risk_types
    assert RiskType.LONG_LEAD_TIME in risk_types
    assert RiskType.HIGH_MOQ in risk_types
