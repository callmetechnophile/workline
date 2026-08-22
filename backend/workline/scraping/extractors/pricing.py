"""Pricing and stock extractor from raw vendor text."""

import re
from typing import List, Optional, Tuple
from backend.workline.scraping.models import QuantityBreak


class PricingExtractor:
    """Parses raw price strings, currency symbols, and quantity price breaks."""

    CURRENCY_SYMBOLS = {
        "$": "USD",
        "₹": "INR",
        "rs": "INR",
        "inr": "INR",
        "€": "EUR",
        "£": "GBP",
    }

    def parse_price(self, price_raw: Optional[str], default_currency: str = "INR") -> Tuple[Optional[float], str]:
        if not price_raw:
            return None, default_currency

        text = price_raw.strip()
        currency = default_currency

        # Detect currency
        for sym, curr in self.CURRENCY_SYMBOLS.items():
            if sym in text.lower():
                currency = curr
                break

        # Remove currency symbols and non-numeric chars except dot
        clean_num = re.sub(r'[^0-9.]', '', text)
        if not clean_num:
            return None, currency

        try:
            return float(clean_num), currency
        except ValueError:
            return None, currency

    def parse_stock(self, stock_raw: Optional[str]) -> Tuple[Optional[int], bool]:
        if not stock_raw:
            return None, False

        text = stock_raw.strip().lower()
        if "in stock" in text or "available" in text:
            # Check for numeric count
            num_match = re.search(r'([0-9,]+)', text)
            if num_match:
                try:
                    count = int(num_match.group(1).replace(",", ""))
                    return count, count > 0
                except ValueError:
                    pass
            return 100, True

        num_match = re.search(r'([0-9,]+)', text)
        if num_match:
            try:
                count = int(num_match.group(1).replace(",", ""))
                return count, count > 0
            except ValueError:
                pass

        if "out of stock" in text or "backorder" in text:
            return 0, False

        return None, False
