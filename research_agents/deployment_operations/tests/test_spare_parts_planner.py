"""Tests for spare parts planner."""
from research_agents.deployment_operations.services.spare_parts_planner import SparePartsPlanner


def test_spare_parts_with_handoff():
    planner = SparePartsPlanner()
    handoff = {
        "parts": [
            {"part_id": "CHIP-01", "part_name": "RF Transceiver", "is_single_source": True, "lead_time_weeks": 20.0},
            {"part_id": "RES-02", "part_name": "Standard Resistor", "is_single_source": False, "lead_time_weeks": 2.0},
        ]
    }
    spares = planner.plan_spares(handoff)
    assert len(spares) == 2
    rf_spare = next(s for s in spares if s.part_id == "CHIP-01")
    assert rf_spare.is_critical is True
    assert rf_spare.sourcing_risk_level == "HIGH"
