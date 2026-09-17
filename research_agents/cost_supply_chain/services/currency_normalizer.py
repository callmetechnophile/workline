"""
Currency normalization, FX conversions, and exchange rate buffer service.
"""

from typing import Dict, Optional, Tuple
from loguru import logger
from research_agents.cost_supply_chain.config import FX_UNKNOWN, config


class CurrencyNormalizer:
    """Normalizes monetary values across supported currencies."""

    def __init__(self, exchange_rates: Optional[Dict[str, float]] = None):
        self.rates = exchange_rates or config.currencies.exchange_rates_to_usd

    def convert(
        self, amount: float, from_currency: str, to_currency: str = "USD"
    ) -> Tuple[float, str]:
        """
        Convert amount from source to target currency.
        Returns (converted_amount, status_code).
        Status is 'OK' or FX_UNKNOWN.
        """
        src = from_currency.upper()
        dst = to_currency.upper()

        if src == dst:
            return round(amount, 4), "OK"

        if src not in self.rates or dst not in self.rates:
            logger.warning(f"Unsupported currency conversion: {src} -> {dst}")
            return amount, FX_UNKNOWN

        # Rate is USD value per 1 unit of foreign currency
        amount_in_usd = amount * self.rates[src]
        converted = amount_in_usd / self.rates[dst]
        return round(converted, 4), "OK"

    def get_currency_risk_buffer(
        self, amount: float, currency: str, buffer_pct: Optional[float] = None
    ) -> float:
        """Calculate FX volatility risk buffer."""
        if currency.upper() == config.default_currency:
            return 0.0
        pct = buffer_pct or config.risk_thresholds.currency_fluctuation_buffer_pct
        return round(amount * (pct / 100.0), 4)
