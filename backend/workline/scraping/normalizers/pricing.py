"""Pricing normalizer and currency converter."""

from typing import Dict, Optional


class PricingNormalizer:
    """Normalizes pricing across currencies to base currency (INR)."""

    # Baseline exchange rates
    EXCHANGE_RATES: Dict[str, float] = {
        "INR": 1.0,
        "USD": 86.5,
        "EUR": 91.0,
        "GBP": 109.0,
    }

    def convert_to_inr(self, amount: Optional[float], currency: str) -> Optional[float]:
        if amount is None:
            return None
        rate = self.EXCHANGE_RATES.get(currency.upper(), 1.0)
        return round(amount * rate, 2)

    def convert(self, amount: Optional[float], from_currency: str, to_currency: str) -> Optional[float]:
        if amount is None:
            return None
        inr = self.convert_to_inr(amount, from_currency)
        if inr is None:
            return None
        target_rate = self.EXCHANGE_RATES.get(to_currency.upper(), 1.0)
        return round(inr / target_rate, 2)
