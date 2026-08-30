"""
Unit tests for OrderConsolidator and shipping allocation (Sections 19, 20, 26).
"""

import pytest
from research_agents.bom_optimization_agent.schemas import Location, SupplierOffer
from research_agents.bom_optimization_agent.services.order_consolidator import OrderConsolidator


@pytest.mark.asyncio
async def test_order_consolidation_and_shipping_allocation():
    consolidator = OrderConsolidator()
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
            data_timestamp="2026-08-30",
        ),
        SupplierOffer(
            supplier_id="SUPP-ROBU",
            supplier_name="Robu.in",
            location=Location(city="Pune", state="Maharashtra"),
            bom_item_id="BOM-002",
            part_number="ESP32-S3-WROOM-1",
            manufacturer="Espressif",
            unit_price=420.0,
            data_timestamp="2026-08-30",
        ),
    ]

    bom_items = [
        {"bom_item_id": "BOM-001", "component_name": "Jetson Orin Nano", "quantity": 1},
        {"bom_item_id": "BOM-002", "component_name": "ESP32-S3", "quantity": 1},
    ]

    orders = await consolidator.consolidate_orders(offers, bom_items, destination, shipping_mode="surface")

    assert len(orders) == 1
    order = orders[0]
    assert order.supplier_id == "SUPP-ROBU"
    assert len(order.items) == 2
    assert order.product_subtotal == 45420.0
    assert order.shipping_cost > 0
    assert order.known_landed_cost == round(order.product_subtotal + order.shipping_cost, 2)

    # Verify shipping allocation
    assert order.items[0].shipping_cost_allocated is not None
    assert order.items[1].shipping_cost_allocated is not None
    total_alloc = round(order.items[0].shipping_cost_allocated + order.items[1].shipping_cost_allocated, 2)
    assert abs(total_alloc - order.shipping_cost) <= 0.05
