"""
Unit tests for StrategyGenerator (Sections 22, 23, 24, 31, 32).
"""

import pytest
from research_agents.bom_optimization_agent.schemas import Location, ProjectConstraints, SupplierOffer
from research_agents.bom_optimization_agent.services.strategy_generator import StrategyGenerator


@pytest.mark.asyncio
async def test_strategy_generation_and_constraint_handling():
    generator = StrategyGenerator()
    destination = Location(city="Bengaluru", state="Karnataka")

    offers = [
        SupplierOffer(
            supplier_id="SUPP-ROBU",
            supplier_name="Robu.in",
            location=Location(city="Pune", state="Maharashtra"),
            bom_item_id="BOM-001",
            part_number="900-13766-0000-000",
            manufacturer="NVIDIA",
            unit_price=45000.0,
            lead_time_days=2,
            data_timestamp="2026-08-30",
        ),
        SupplierOffer(
            supplier_id="SUPP-MOUSER",
            supplier_name="Mouser",
            location=Location(city="Bengaluru", state="Karnataka"),
            bom_item_id="BOM-001",
            part_number="900-13766-0000-000",
            manufacturer="NVIDIA",
            unit_price=44000.0,
            lead_time_days=4,
            data_timestamp="2026-08-30",
        ),
    ]

    bom_items = [{"bom_item_id": "BOM-001", "part_number": "900-13766-0000-000", "component_name": "Jetson Orin", "quantity": 1}]

    # Case 1: Unconstrained
    selected_strat, all_strats, opt_items = await generator.generate_strategies(
        offers, bom_items, destination, ProjectConstraints()
    )

    assert len(all_strats) == 4
    strat_names = {s.name for s in all_strats}
    assert "Lowest Landed Cost" in strat_names
    assert "Fastest Delivery" in strat_names
    assert "Minimum Number of Suppliers" in strat_names
    assert "Balanced Cost + Delivery" in strat_names

    assert len(opt_items) == 1
    assert selected_strat.name == "Lowest Landed Cost"

    # Case 2: Tight delivery constraint requiring fastest option
    tight_constraints = ProjectConstraints(maximum_delivery_days=2)
    selected_tight, _, _ = await generator.generate_strategies(
        offers, bom_items, destination, tight_constraints
    )
    assert selected_tight.estimated_delivery_days is not None
