"""Unit tests for shipping calculations, currency conversion, and multi-vendor landed cost optimization."""

import pytest
from backend.workline.procurement.models import (
    ComponentRequirement,
)
from backend.workline.procurement.optimize import ProcurementOptimizer
from backend.workline.procurement.shipping import ShippingCalculator
from backend.workline.scraping.models import (
    RawVendorResult,
)
from backend.workline.scraping.normalizers.component import ComponentNormalizer
from backend.workline.scraping.normalizers.pricing import PricingNormalizer


def test_pricing_normalizer_conversion():
    """Test currency conversions to INR."""
    p_norm = PricingNormalizer()
    assert p_norm.convert_to_inr(100.0, "INR") == 100.0
    assert p_norm.convert_to_inr(10.0, "USD") == 865.0


def test_shipping_calculator():
    """Test freight estimation and free threshold rules."""
    calc = ShippingCalculator()
    # Domestic (Robu)
    sh_robu_below = calc.estimate_shipping("Robu", 500.0)
    assert sh_robu_below.estimated_cost == 90.0
    assert sh_robu_below.confidence == "ESTIMATED"

    sh_robu_above = calc.estimate_shipping("Robu", 2000.0)
    assert sh_robu_above.estimated_cost == 0.0


def test_procurement_optimizer_options():
    """Test generation of multi-vendor optimization options."""
    optimizer = ProcurementOptimizer()
    normalizer = ComponentNormalizer()

    # Raw results
    raw_mcu = RawVendorResult(
        vendor="Robocraze",
        source_url="https://robocraze.com",
        product_url="https://robocraze.com/esp32",
        product_name="ESP32-S3 DevKit",
        manufacturer="Espressif",
        mpn="ESP32-S3-DevKitC-1",
        price_raw="680.00",
        currency="INR",
        stock_raw="50",
    )
    raw_sensor = RawVendorResult(
        vendor="Robu",
        source_url="https://robu.in",
        product_url="https://robu.in/bme280",
        product_name="BME280 Sensor Module",
        manufacturer="Bosch",
        mpn="BME280",
        price_raw="349.00",
        currency="INR",
        stock_raw="100",
    )

    cands_mcu = normalizer.normalize([raw_mcu])
    cands_sensor = normalizer.normalize([raw_sensor])

    reqs = [
        ComponentRequirement(requirement_id="req_mcu", category="Microcontroller", quantity=1),
        ComponentRequirement(requirement_id="req_sensor", category="Sensors & Environmental", quantity=1),
    ]

    candidate_map = {
        "req_mcu": cands_mcu,
        "req_sensor": cands_sensor,
    }

    plan = optimizer.optimize_procurement("test_proj", reqs, candidate_map)
    assert plan.project_id == "test_proj"
    assert plan.recommended_option is not None
    assert plan.recommended_option.total_component_cost > 0.0
    assert plan.recommended_option.estimated_landed_total >= plan.recommended_option.total_component_cost
    assert len(plan.alternative_options) >= 1
