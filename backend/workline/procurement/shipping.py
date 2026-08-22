"""Shipping and landed cost calculation with explicit confidence labeling."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ShippingEstimate(BaseModel):
    """Freight and logistics estimate."""
    origin: str
    destination: str
    carrier: str
    service: str
    estimated_cost: float
    currency: str = "INR"
    confidence: str = "ESTIMATED"           # ESTIMATED, UNKNOWN, EXACT
    source: str = "Vendor Freight Schedule"


class ShippingCalculator:
    """Calculates shipping and landed cost estimates for selected vendors."""

    # Baseline vendor shipping rules
    VENDOR_SHIPPING_RULES: Dict[str, Dict[str, Any]] = {
        "Robu": {
            "carrier": "Blue Dart / DTDC",
            "service": "Standard Express Domestic",
            "base_cost_inr": 90.0,
            "free_threshold_inr": 1500.0,
            "origin": "Pune, India",
        },
        "Robocraze": {
            "carrier": "Delhivery / DTDC",
            "service": "Surface Express Domestic",
            "base_cost_inr": 80.0,
            "free_threshold_inr": 1000.0,
            "origin": "Bangalore, India",
        },
        "DigiKey": {
            "carrier": "DHL Express International",
            "service": "Worldwide Priority",
            "base_cost_inr": 1450.0,
            "free_threshold_inr": 4500.0,
            "origin": "Thief River Falls, USA",
        },
        "Mouser": {
            "carrier": "FedEx International",
            "service": "International Priority",
            "base_cost_inr": 1600.0,
            "free_threshold_inr": 4200.0,
            "origin": "Mansfield, Texas, USA",
        },
    }

    def estimate_shipping(
        self,
        vendor: str,
        total_subtotal_inr: float,
        destination: str = "India",
    ) -> ShippingEstimate:
        rule = self.VENDOR_SHIPPING_RULES.get(vendor)
        if not rule:
            return ShippingEstimate(
                origin="Unknown",
                destination=destination,
                carrier="Standard Freight",
                service="Standard Delivery",
                estimated_cost=250.0,
                confidence="UNKNOWN",
                source="Fallback Default",
            )

        if total_subtotal_inr >= rule["free_threshold_inr"]:
            cost = 0.0
            confidence = "ESTIMATED"
        else:
            cost = rule["base_cost_inr"]
            confidence = "ESTIMATED"

        return ShippingEstimate(
            origin=rule["origin"],
            destination=destination,
            carrier=rule["carrier"],
            service=rule["service"],
            estimated_cost=cost,
            currency="INR",
            confidence=confidence,
            source="Vendor Freight Schedule Baseline",
        )
