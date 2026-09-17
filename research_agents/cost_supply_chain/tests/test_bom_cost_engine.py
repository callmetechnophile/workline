"""Tests for BOM cost rollup engine and zero-fabrication guarantees."""
import pytest
from research_agents.cost_supply_chain.config import PRICE_UNKNOWN
from research_agents.cost_supply_chain.schemas import CostBreakdown, PartCost, VolumeTier
from research_agents.cost_supply_chain.services.bom_cost_engine import BOMCostEngine


def test_rollup_simple():
    engine = BOMCostEngine()
    parts = [
        PartCost(part_id="P1", part_name="Resistor", quantity_per_assembly=4, unit_cost=0.50),
        PartCost(part_id="P2", part_name="Capacitor", quantity_per_assembly=2, unit_cost=1.50),
    ]
    rollup = engine.rollup_bom_cost("BOM-1", "PROJ-1", parts, target_volume=100)
    assert rollup.is_cost_complete is True
    assert rollup.unpriced_parts_count == 0
    # 4*0.50 + 2*1.50 = 2.0 + 3.0 = 5.0
    assert rollup.total_unit_cost == 5.0
    assert rollup.total_extended_cost == 500.0


def test_zero_fabrication_unpriced_parts():
    engine = BOMCostEngine()
    parts = [
        PartCost(part_id="P1", part_name="Known Chip", quantity_per_assembly=1, unit_cost=10.0),
        PartCost(part_id="P2", part_name="Custom ASIC", quantity_per_assembly=1, unit_cost=None, price_status=PRICE_UNKNOWN),
    ]
    rollup = engine.rollup_bom_cost("BOM-2", "PROJ-1", parts)
    assert rollup.is_cost_complete is False
    assert rollup.unpriced_parts_count == 1
    assert "P2" in rollup.unpriced_part_ids
    # Does NOT fabricate a price for P2
    assert rollup.total_unit_cost == 10.0


def test_volume_tiers():
    engine = BOMCostEngine()
    parts = [
        PartCost(
            part_id="P1",
            part_name="Sensor",
            quantity_per_assembly=1,
            unit_cost=25.0,
            volume_tiers=[
                VolumeTier(min_quantity=100, unit_cost=20.0),
                VolumeTier(min_quantity=1000, unit_cost=15.0),
            ],
        )
    ]
    rollup_1000 = engine.rollup_bom_cost("BOM-3", "PROJ-1", parts, target_volume=1000)
    assert rollup_1000.total_unit_cost == 15.0

    rollup_50 = engine.rollup_bom_cost("BOM-3", "PROJ-1", parts, target_volume=50)
    assert rollup_50.total_unit_cost == 25.0


def test_volume_cost_curve():
    engine = BOMCostEngine()
    parts = [
        PartCost(
            part_id="P1",
            part_name="Housing",
            quantity_per_assembly=1,
            unit_cost=50.0,
            breakdown=CostBreakdown(tooling_nre=10000.0),
        )
    ]
    rollup = engine.rollup_bom_cost("BOM-4", "PROJ-1", parts)
    curve = engine.generate_volume_cost_curve(rollup, quantities=[100, 1000, 10000])
    assert len(curve.curve_points) == 3
    # At 100 units, tooling adds 10000/100 = 100/unit
    assert curve.curve_points[0].unit_cost > curve.curve_points[1].unit_cost
