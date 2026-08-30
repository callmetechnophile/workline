"""
Shipping calculator interface for BOMOptimizationAgent (Sections 13 & 18).
"""

from abc import ABC, abstractmethod
from typing import Optional
from research_agents.bom_optimization_agent.schemas import Location, ShippingOption


class ShippingCalculator(ABC):
    """Abstract interface for carrier shipping quote estimation."""

    @abstractmethod
    async def calculate_shipping(
        self,
        supplier_id: str,
        origin: Location,
        destination: Location,
        shipment_weight_kg: float = 0.5,
        shipping_mode: str = "surface",
    ) -> ShippingOption:
        """Calculates transit cost, distance, and estimated delivery days."""
        pass
