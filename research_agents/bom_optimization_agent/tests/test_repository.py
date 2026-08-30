"""
Unit tests for ProcurementOptimizationRepository interface (Section 41).
"""

import pytest
from research_agents.bom_optimization_agent.repository import InMemoryProcurementOptimizationRepository
from research_agents.bom_optimization_agent.schemas import (
    BOMOptimizationAgentOutput,
    ProcurementStrategy,
    ShippingOption,
    SupplierOffer,
    SupplierOrder,
)


@pytest.mark.asyncio
async def test_procurement_repository_all_methods():
    repo = InMemoryProcurementOptimizationRepository()
    proj_id = "proj_test_proc_01"

    # 1. Save Supplier Offer
    await repo.save_supplier_offer(
        SupplierOffer(
            supplier_id="SUPP-1",
            supplier_name="Robu",
            bom_item_id="BOM-01",
            part_number="ESP32",
            manufacturer="Espressif",
            data_timestamp="2026-08-30",
        ),
        proj_id,
    )

    # 2. Save Shipping Option
    await repo.save_shipping_option(
        ShippingOption(
            shipping_id="SHIP-01",
            supplier_id="SUPP-1",
            origin="Pune",
            destination="Bengaluru",
            data_timestamp="2026-08-30",
        ),
        proj_id,
    )

    # 3. Save Order
    await repo.save_order(
        SupplierOrder(
            order_id="ORD-01",
            supplier_id="SUPP-1",
            supplier_name="Robu",
        ),
        proj_id,
    )

    # 4. Save Strategy
    await repo.save_strategy(
        ProcurementStrategy(
            strategy_id="STRAT-01",
            name="Cheapest",
            objective="minimize_landed_cost",
        ),
        proj_id,
    )

    # 5. Save Procurement Warning
    await repo.save_procurement_warning("Lead time exceeds 5 days", proj_id)

    # 6. Save Full Output
    output = BOMOptimizationAgentOutput(
        project_id=proj_id,
        bom_id="BOM-01",
        optimization_id="OPT-01",
    )
    saved_id = await repo.save_optimization(output)
    assert saved_id == proj_id

    retrieved = await repo.get_optimization(proj_id)
    assert retrieved is not None
    assert retrieved.optimization_id == "OPT-01"
