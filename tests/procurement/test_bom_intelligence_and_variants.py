"""Tests for BOM Generation, Part Resolution, and Variant Ambiguity."""

import pytest
from backend.workline.procurement.models import BomStatus, ProcurementStatus
from backend.workline.procurement.part_resolver import PartResolver
from backend.workline.procurement.service import ProcurementIntelligenceService


def test_bom_creation_and_item_addition():
    """Test 1-3: BOM creation, reference designators, and totals."""
    service = ProcurementIntelligenceService()
    bom = service.create_bom(bom_id="BOM-TEST-01", project_id="rover_v2")
    assert bom.bom_id == "BOM-TEST-01"
    assert bom.status == BomStatus.DRAFT

    item = service.add_bom_item(
        bom_id="BOM-TEST-01",
        reference_designator="U1",
        part_number="TPS62130",
        quantity=2,
    )
    assert item.reference_designator == "U1"
    assert item.part_number == "TPS62130"
    assert item.stock == 500
    assert bom.estimated_total > 0


def test_part_variant_resolution():
    """Test 6-9: Exact vs Ambiguous Part Variant resolution."""
    # LM2596 has 1 variant -> exact match
    resolved, exact, variants, ambiguous = PartResolver.resolve("LM2596")
    assert resolved is True
    assert exact is not None
    assert exact.ordering_code == "LM2596S-5.0/NOPB"
    assert ambiguous is False

    # TPS62130 has multiple packaging variants -> ambiguous
    resolved_tps, exact_tps, variants_tps, ambiguous_tps = PartResolver.resolve("TPS62130")
    assert resolved_tps is False
    assert len(variants_tps) == 2
    assert ambiguous_tps is True
    codes = [v.ordering_code for v in variants_tps]
    assert "TPS62130RGTR" in codes
    assert "TPS62130RGTT" in codes


def test_bom_validation():
    """Test 24-28: BOM readiness validation."""
    service = ProcurementIntelligenceService()
    bom = service.create_bom(bom_id="BOM-VAL-01", project_id="rover_v2")

    # Add available item
    service.add_bom_item(
        bom_id="BOM-VAL-01",
        reference_designator="U1",
        part_number="TPS62130",
        quantity=1,
    )

    status, issues = service.validate_bom("BOM-VAL-01")
    assert status == BomStatus.READY_FOR_PROCUREMENT
    assert len(issues) == 0
