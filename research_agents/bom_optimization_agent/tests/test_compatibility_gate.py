"""
Unit tests for TechnicalCompatibilityGate (Sections 9 & 10).
"""

from research_agents.bom_optimization_agent.schemas import Location, SupplierOffer
from research_agents.bom_optimization_agent.services.compatibility_gate import TechnicalCompatibilityGate


def test_compatibility_gate_filtering():
    gate = TechnicalCompatibilityGate()

    bom_items = [
        {"bom_item_id": "BOM-001", "part_number": "ESP32-S3-WROOM-1-N8R8", "component_name": "ESP32-S3"}
    ]
    approved_alternatives = [
        {"alternative_id": "ALT-001", "part_number": "STM32F405RGT6", "compatibility": "electrically_compatible"}
    ]

    offers = [
        # Approved BOM part
        SupplierOffer(
            supplier_id="SUPP-1",
            supplier_name="Distributor A",
            bom_item_id="BOM-001",
            part_number="ESP32-S3-WROOM-1-N8R8",
            manufacturer="Espressif",
            unit_price=400.0,
            data_timestamp="2026-08-30",
        ),
        # Approved alternative part
        SupplierOffer(
            supplier_id="SUPP-2",
            supplier_name="Distributor B",
            bom_item_id="BOM-001",
            part_number="STM32F405RGT6",
            manufacturer="STMicroelectronics",
            unit_price=350.0,
            data_timestamp="2026-08-30",
        ),
        # Incompatible / unverified part
        SupplierOffer(
            supplier_id="SUPP-3",
            supplier_name="Distributor C",
            bom_item_id="BOM-001",
            part_number="ATmega328P-PU",
            manufacturer="Microchip",
            unit_price=150.0,
            data_timestamp="2026-08-30",
        ),
    ]

    compatible, warnings = gate.filter_compatible_offers(offers, bom_items, approved_alternatives)

    assert len(compatible) == 2
    comp_parts = {o.part_number for o in compatible}
    assert "ESP32-S3-WROOM-1-N8R8" in comp_parts
    assert "STM32F405RGT6" in comp_parts
    assert "ATmega328P-PU" not in comp_parts
    assert any("ATmega328P-PU" in w for w in warnings)
