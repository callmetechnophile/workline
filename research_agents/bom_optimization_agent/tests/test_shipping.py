"""
Unit tests for BlueDartShippingProvider and DistanceMatrixService (Sections 14, 15, 18).
"""

import pytest
from research_agents.bom_optimization_agent.adapters.shipping.bluedart import BlueDartShippingProvider
from research_agents.bom_optimization_agent.adapters.shipping.distance import DistanceMatrixService
from research_agents.bom_optimization_agent.schemas import Location


@pytest.mark.asyncio
async def test_bluedart_shipping_calculations():
    dist_service = DistanceMatrixService()
    provider = BlueDartShippingProvider(distance_service=dist_service)

    pune = Location(city="Pune", state="Maharashtra")
    bengaluru = Location(city="Bengaluru", state="Karnataka")

    # Distance check
    dist = dist_service.get_distance_km(pune, bengaluru)
    assert dist == 840.0

    # Surface economy shipping quote
    surface_opt = await provider.calculate_shipping("SUPP-ROBU", pune, bengaluru, shipment_weight_kg=0.8, shipping_mode="surface")
    assert surface_opt.carrier == "Blue Dart"
    assert surface_opt.shipping_mode == "surface"
    assert surface_opt.shipping_cost > 90.0
    assert surface_opt.source == "configured_estimate"
    assert surface_opt.estimated_delivery_days in (2, 3)

    # Air express shipping quote
    air_opt = await provider.calculate_shipping("SUPP-ROBU", pune, bengaluru, shipment_weight_kg=0.8, shipping_mode="express")
    assert air_opt.shipping_mode == "express"
    assert air_opt.shipping_cost > surface_opt.shipping_cost
    assert air_opt.estimated_delivery_days <= 2
