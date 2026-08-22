"""Unit tests for MPN normalization, duplicate consolidation, datasheet validation, and deterministic compatibility."""

import pytest
from backend.workline.procurement.models import (
    CheckStatus,
    ComponentRequirement,
)
from backend.workline.procurement.validate import TechnicalValidator
from backend.workline.scraping.models import (
    DatasheetMetadata,
    DatasheetStatus,
    RawVendorResult,
)
from backend.workline.scraping.normalizers.component import (
    ComponentNormalizer,
    generate_component_id,
    normalize_mpn,
)
from backend.workline.scraping.validators.datasheet import DatasheetValidator


def test_mpn_normalization_and_id_generation():
    """Test canonical component ID construction from Manufacturer + MPN."""
    assert normalize_mpn("  TPS62130RGTR  ") == "TPS62130RGTR"
    cid = generate_component_id("Texas Instruments", "TPS62130RGTR")
    assert cid == "component:texas_instruments_tps62130rgtr"


def test_duplicate_component_consolidation():
    """Test that multiple vendors offering the same MPN resolve to a single ComponentCandidate with multiple listings."""
    raw1 = RawVendorResult(
        vendor="DigiKey",
        source_url="https://digikey.com",
        product_url="https://digikey.com/tps",
        product_name="Step-Down Converter",
        manufacturer="Texas Instruments",
        mpn="TPS62130RGTR",
        price_raw="2.50",
        currency="USD",
    )
    raw2 = RawVendorResult(
        vendor="Mouser",
        source_url="https://mouser.com",
        product_url="https://mouser.com/tps",
        product_name="Switching Regulators",
        manufacturer="Texas Instruments",
        mpn="TPS62130RGTR",
        price_raw="210.00",
        currency="INR",
    )

    normalizer = ComponentNormalizer()
    candidates = normalizer.normalize([raw1, raw2])

    assert len(candidates) == 1
    c = candidates[0]
    assert c.component_id == "component:texas_instruments_tps62130rgtr"
    assert len(c.listings) == 2
    vendors = [l.vendor_name for l in c.listings]
    assert "DigiKey" in vendors
    assert "Mouser" in vendors


def test_datasheet_validation():
    """Test datasheet validation logic."""
    val = DatasheetValidator()
    meta = DatasheetMetadata(
        datasheet_id="ds_1",
        url="https://www.ti.com/lit/ds/symlink/tps62130.pdf",
        manufacturer="Texas Instruments",
        mpn="TPS62130",
    )
    status, msg = val.validate_datasheet(meta)
    assert status == DatasheetStatus.VERIFIED


def test_deterministic_voltage_and_current_validation():
    """Test deterministic electrical compatibility rules."""
    validator = TechnicalValidator()
    normalizer = ComponentNormalizer()

    raw = RawVendorResult(
        vendor="DigiKey",
        source_url="https://digikey.com",
        product_url="https://digikey.com/p",
        product_name="3A Step-Down Converter",
        manufacturer="Texas Instruments",
        mpn="TPS62130RGTR",
        spec_table={
            "Voltage - Input (Min)": "3V",
            "Voltage - Input (Max)": "17V",
            "Voltage - Output (Nom)": "3.3V",
            "Current - Output": "3A",
        },
    )
    cand = normalizer.normalize([raw])[0]

    # Matching requirement -> PASS
    req_pass = ComponentRequirement(
        requirement_id="req_reg",
        category="Voltage Regulator",
        nominal_voltage=3.3,
        required_current_min_a=2.0,
    )
    report_pass = validator.validate(cand, req_pass)
    assert report_pass.is_compatible is True
    assert report_pass.overall_status == CheckStatus.PASS

    # Incompatible voltage -> FAIL
    req_fail_v = ComponentRequirement(
        requirement_id="req_reg",
        category="Voltage Regulator",
        nominal_voltage=1.8,
        required_current_min_a=2.0,
    )
    report_fail_v = validator.validate(cand, req_fail_v)
    assert report_fail_v.is_compatible is False
    assert report_fail_v.overall_status == CheckStatus.FAIL

    # Incompatible current capacity -> FAIL
    req_fail_i = ComponentRequirement(
        requirement_id="req_reg",
        category="Voltage Regulator",
        nominal_voltage=3.3,
        required_current_min_a=5.0,  # 5A required, only 3A provided
    )
    report_fail_i = validator.validate(cand, req_fail_i)
    assert report_fail_i.is_compatible is False
    assert report_fail_i.overall_status == CheckStatus.FAIL
