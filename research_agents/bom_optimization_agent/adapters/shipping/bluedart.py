"""
Blue Dart logistics provider implementation for BOMOptimizationAgent (Sections 14 & 18).
Models Express (Air) and Surface (Road) domestic shipping costs within India.
"""

import uuid
from research_agents.bom_optimization_agent.adapters.shipping.base import ShippingCalculator
from research_agents.bom_optimization_agent.adapters.shipping.distance import DistanceMatrixService
from research_agents.bom_optimization_agent.schemas import Location, ShippingOption


class BlueDartShippingProvider(ShippingCalculator):
    """Calculates realistic Blue Dart Express and Surface shipping cost estimates."""

    def __init__(self, distance_service: DistanceMatrixService = None):
        self.distance_service = distance_service or DistanceMatrixService()

    async def calculate_shipping(
        self,
        supplier_id: str,
        origin: Location,
        destination: Location,
        shipment_weight_kg: float = 0.5,
        shipping_mode: str = "surface",
    ) -> ShippingOption:
        dist_km = self.distance_service.get_distance_km(origin, destination)
        is_local = (origin.city or "").lower() == (destination.city or "").lower()

        mode_lower = shipping_mode.lower()

        if mode_lower in ("express", "air", "priority"):
            # Blue Dart Air Express rate model: base ₹220 for first 500g + distance tier
            service_name = "Apex (Air Express)"
            if is_local:
                cost = 120.0
                delivery_days = 1
            else:
                base_air = 220.0
                weight_mult = max(1.0, shipment_weight_kg / 0.5)
                dist_factor = 1.0 + (dist_km / 2500.0) * 0.4
                cost = round(base_air * weight_mult * dist_factor, 2)
                delivery_days = 1 if dist_km < 1000 else 2
        else:
            # Blue Dart Surface/Economy rate model: base ₹90 for first 500g + distance factor
            service_name = "Surfaceline (Economy)"
            if is_local:
                cost = 70.0
                delivery_days = 1
            else:
                base_surface = 90.0
                weight_mult = max(1.0, shipment_weight_kg / 0.5)
                dist_factor = 1.0 + (dist_km / 2000.0) * 0.5
                cost = round(base_surface * weight_mult * dist_factor, 2)
                delivery_days = 2 if dist_km < 600 else (3 if dist_km < 1200 else 5)

        return ShippingOption(
            shipping_id=f"SHIP-{uuid.uuid4().hex[:6].upper()}",
            supplier_id=supplier_id,
            origin=f"{origin.city}, {origin.state}",
            destination=f"{destination.city}, {destination.state}",
            distance_km=dist_km,
            carrier="Blue Dart",
            service=service_name,
            shipping_mode="express" if mode_lower in ("express", "air", "priority") else "surface",
            shipping_cost=cost,
            currency="INR",
            estimated_delivery_days=delivery_days,
            source="configured_estimate",  # Explicitly marked as configured estimate per Section 14
            data_timestamp="2026-08-30T12:00:00Z",
            confidence=0.92,
        )
