"""Pricing calculations, quantity breaks, and currency normalization."""

from typing import List, Optional
from backend.workline.procurement.models import QuantityBreak, SupplierOffer


class PriceCalculator:
    """Calculates pricing based on quantity breaks and currency rates."""

    DEFAULT_EXCHANGE_RATES = {
        "USD": 83.5,
        "EUR": 90.2,
        "INR": 1.0,
    }

    @classmethod
    def get_unit_price(cls, offer: SupplierOffer, quantity: int) -> float:
        if not offer.quantity_breaks:
            return offer.unit_price

        sorted_breaks = sorted(offer.quantity_breaks, key=lambda q: q.quantity, reverse=True)
        for qb in sorted_breaks:
            if quantity >= qb.quantity:
                return qb.unit_price

        return offer.unit_price

    @classmethod
    def normalize_price(
        cls, price: float, from_currency: str, to_currency: str = "INR"
    ) -> float:
        rate_from = cls.DEFAULT_EXCHANGE_RATES.get(from_currency.upper(), 1.0)
        rate_to = cls.DEFAULT_EXCHANGE_RATES.get(to_currency.upper(), 1.0)
        in_inr = price * rate_from
        return round(in_inr / rate_to, 2)
