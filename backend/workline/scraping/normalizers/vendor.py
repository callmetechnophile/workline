"""Vendor listing normalizer."""

import re
import uuid
from backend.workline.scraping.extractors.pricing import PricingExtractor
from backend.workline.scraping.models import (
    FreshnessStatus,
    RawVendorResult,
    VendorListing,
)
from backend.workline.scraping.normalizers.pricing import PricingNormalizer


class VendorNormalizer:
    """Transforms raw vendor results into structured VendorListing models."""

    def __init__(self):
        self.pricing_extractor = PricingExtractor()
        self.pricing_normalizer = PricingNormalizer()

    def normalize_listing(self, raw: RawVendorResult) -> VendorListing:
        price_val, curr = self.pricing_extractor.parse_price(
            raw.price_raw, default_currency=raw.currency or "INR"
        )
        stock_val, in_stock = self.pricing_extractor.parse_stock(raw.stock_raw)

        # Parse lead time
        lead_days = None
        if raw.lead_time_raw:
            lt_match = re.search(r'([0-9]+)', raw.lead_time_raw)
            if lt_match:
                try:
                    lead_days = int(lt_match.group(1))
                except ValueError:
                    pass

        # Location
        location = "Global / US"
        if raw.vendor in ("Robu", "Robocraze"):
            location = "India"

        listing_id = f"listing:{raw.vendor.lower()}_{re.sub(r'[^a-zA-Z0-9]', '_', raw.mpn or raw.product_name).lower()}"

        return VendorListing(
            listing_id=listing_id,
            vendor_name=raw.vendor,
            product_url=raw.product_url,
            sku=raw.sku,
            unit_price=price_val,
            currency=curr,
            stock=stock_val,
            in_stock=in_stock,
            lead_time_days=lead_days,
            location=location,
            freshness=FreshnessStatus.FRESH,
            retrieved_at=raw.retrieved_at,
            raw_metadata=raw.raw_metadata,
        )
