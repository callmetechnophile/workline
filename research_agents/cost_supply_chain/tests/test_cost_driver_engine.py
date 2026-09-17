"""Tests for cost driver extraction and DFM/DFA handoffs."""
from research_agents.cost_supply_chain.services.cost_driver_engine import CostDriverEngine


def test_dfm_handoff():
    engine = CostDriverEngine()
    findings = [
        {"rule_id": "TOL-001", "finding": "Tight pocket tolerance requiring EDM", "severity": "HIGH"},
        {"rule_id": "RAD-002", "finding": "Small internal corner radius", "severity": "MEDIUM"},
    ]
    drivers = engine.extract_from_dfm_handoff(findings, base_unit_cost=100.0)
    assert len(drivers) == 2
    assert drivers[0].driver_id == "DFM-DRV-01"
    assert drivers[0].cost_per_unit == 8.0  # 8% of 100.0


def test_dfa_handoff():
    engine = CostDriverEngine()
    metrics = {
        "fastener_count": 16,
        "total_assembly_time_seconds": 360.0,
    }
    drivers = engine.extract_from_dfa_handoff(metrics, base_assembly_cost=20.0)
    assert len(drivers) == 2
    drv_ids = [d.driver_id for d in drivers]
    assert "DFA-DRV-FASTENERS" in drv_ids
    assert "DFA-DRV-CYCLE-TIME" in drv_ids
