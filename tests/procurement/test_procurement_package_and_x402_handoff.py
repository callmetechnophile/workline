"""Tests for Supplier Pricing Breaks, Procurement Package, and x402 Handoff."""

import pytest
from backend.workline.procurement.models import QuantityBreak, SupplierOffer
from backend.workline.procurement.pricing import PriceCalculator
from backend.workline.procurement.service import ProcurementIntelligenceService


def test_quantity_price_breaks():
    """Test 14-17: Volume price breaks and currency normalization."""
    offer = SupplierOffer(
        supplier_id="digikey",
        supplier_item_id="296-1",
        manufacturer="TI",
        part_number="TPS62130",
        ordering_code="TPS62130RGTR",
        description="Regulator",
        package="VQFN-16",
        unit_price=180.0,
        currency="INR",
        quantity_breaks=[
            QuantityBreak(quantity=1, unit_price=180.0),
            QuantityBreak(quantity=10, unit_price=160.0),
            QuantityBreak(quantity=100, unit_price=140.0),
        ],
        stock=1000,
        moq=1,
    )

    # 1 unit -> 180
    assert PriceCalculator.get_unit_price(offer, 1) == 180.0
    # 15 units -> 160
    assert PriceCalculator.get_unit_price(offer, 15) == 160.0
    # 250 units -> 140
    assert PriceCalculator.get_unit_price(offer, 250) == 140.0

    # Currency normalization
    norm_inr = PriceCalculator.normalize_price(10.0, from_currency="USD", to_currency="INR")
    assert norm_inr == 835.0


def test_procurement_package_compilation():
    """Test 29-32: Clean procurement package generation for Phase 5 x402 handoff."""
    service = ProcurementIntelligenceService()
    service.create_bom(bom_id="BOM-PKG-01", project_id="rover_v2")

    service.add_bom_item(
        bom_id="BOM-PKG-01",
        reference_designator="U1",
        part_number="TPS62130",
        quantity=5,
    )
    service.add_bom_item(
        bom_id="BOM-PKG-01",
        reference_designator="U2",
        part_number="LM2596",
        quantity=2,
    )

    pkg = service.generate_procurement_package("BOM-PKG-01")
    assert pkg.bom_id == "BOM-PKG-01"
    assert pkg.validation_status == "READY"
    assert len(pkg.items) == 2
    assert pkg.subtotal > 0
    assert len(pkg.supplier_breakdown) > 0
