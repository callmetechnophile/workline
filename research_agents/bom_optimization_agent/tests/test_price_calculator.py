"""
Unit tests for PriceCalculator (Sections 12, 27, 28).
"""

from research_agents.bom_optimization_agent.schemas import SupplierOffer
from research_agents.bom_optimization_agent.services.price_calculator import PriceCalculator


def test_price_calculator_moq_and_price_breaks():
    calc = PriceCalculator()

    # Case 1: MOQ adjustment
    offer_moq = SupplierOffer(
        supplier_id="SUPP-1",
        supplier_name="Distributor",
        bom_item_id="BOM-001",
        part_number="TPS565208DDCR",
        manufacturer="TI",
        unit_price=80.0,
        minimum_order_quantity=5,
        available_quantity=100,
        data_timestamp="2026-08-30",
    )

    item, in_stock = calc.calculate_item_cost(offer_moq, "Buck Converter", required_quantity=2)
    assert in_stock is True
    assert item.required_quantity == 2
    assert item.purchased_quantity == 5
    assert item.surplus_quantity == 3
    assert item.product_cost == 400.0
    assert "MOQ is 5" in (item.moq_reason or "")

    # Case 2: Price break volume discount
    offer_tiers = SupplierOffer(
        supplier_id="SUPP-1",
        supplier_name="Distributor",
        bom_item_id="BOM-002",
        part_number="ESP32-S3",
        manufacturer="Espressif",
        unit_price=420.0,
        price_breaks={1: 420.0, 10: 380.0, 50: 350.0},
        available_quantity=200,
        data_timestamp="2026-08-30",
    )

    item_10, _ = calc.calculate_item_cost(offer_tiers, "ESP32", required_quantity=10)
    assert item_10.unit_price == 380.0
    assert item_10.product_cost == 3800.0
