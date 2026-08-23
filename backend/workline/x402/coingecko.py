"""
CoinGecko Exchange Rate Client for Workline Informational Reports.

Key Architectural Guarantees:
1. CoinGecko is strictly isolated from payment authorization and settlement logic.
2. Queried ONLY after payment is settled, and ONLY ONCE per report generation.
3. If CoinGecko is unavailable, times out, returns HTTP 5xx, or responds with malformed JSON,
   report compilation continues without failure, annotating the INR field as "Unavailable".
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
import os
from typing import Optional
import httpx
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field


class CoinGeckoRate(BaseModel):
    """Immutable snapshot of the USD Coin -> INR exchange rate at report time."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    available: bool = True
    rate: Optional[float] = None
    rate_decimal: Optional[Decimal] = None
    source: str = "CoinGecko"
    pair: str = "USDC/INR"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_reason: Optional[str] = None


class CoinGeckoClient:
    """Async client for querying CoinGecko prices with strict failure isolation."""

    def __init__(self, timeout_seconds: float = 4.0):
        self.base_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")
        self.timeout = timeout_seconds

    async def fetch_usdc_inr_rate(self) -> CoinGeckoRate:
        """
        Fetches the live USD Coin (USDC) to INR exchange rate once.
        Gracefully handles network partitions, timeouts, HTTP errors, and malformed bodies.
        """
        endpoint = f"{self.base_url}/simple/price"
        params = {"ids": "usd-coin", "vs_currencies": "inr"}
        now_str = datetime.now(timezone.utc).isoformat()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(endpoint, params=params)
                if resp.status_code != 200:
                    logger.warning(f"[CoinGecko] HTTP status {resp.status_code} received from {endpoint}")
                    return CoinGeckoRate(
                        available=False,
                        timestamp=now_str,
                        error_reason=f"CoinGecko service returned HTTP {resp.status_code}",
                    )

                data = resp.json()
                if not isinstance(data, dict) or "usd-coin" not in data or "inr" not in data["usd-coin"]:
                    logger.warning(f"[CoinGecko] Malformed response payload: {data}")
                    return CoinGeckoRate(
                        available=False,
                        timestamp=now_str,
                        error_reason="Malformed response received from exchange rate provider",
                    )

                raw_rate = data["usd-coin"]["inr"]
                rate_dec = Decimal(str(raw_rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                logger.info(f"[CoinGecko] Successfully retrieved 1 USDC ≈ ₹{rate_dec} INR at {now_str}")
                return CoinGeckoRate(
                    available=True,
                    rate=float(rate_dec),
                    rate_decimal=rate_dec,
                    source="CoinGecko",
                    pair="USDC/INR",
                    timestamp=now_str,
                )

        except httpx.TimeoutException:
            logger.warning("[CoinGecko] Request timed out while fetching USD/INR exchange rate")
            return CoinGeckoRate(
                available=False,
                timestamp=now_str,
                error_reason="Exchange-rate service timed out at report generation",
            )
        except Exception as exc:
            logger.warning(f"[CoinGecko] Unexpected error fetching exchange rate: {exc}")
            return CoinGeckoRate(
                available=False,
                timestamp=now_str,
                error_reason=f"Exchange-rate service error: {str(exc)}",
            )


# Singleton instance
coingecko_client = CoinGeckoClient()
