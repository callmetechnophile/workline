"""Universal Scrapling Acquisition and Fallback Provider for Workline Procurement."""

import asyncio
import re
from typing import Any, Dict, List, Optional

from backend.workline.procurement.cache import scrapling_cache
from backend.workline.procurement.models import (
    AvailabilitySpecs,
    CandidateMetadata,
    ComponentCandidate,
    DatasheetInfo,
    DatasheetMetadata,
    DatasheetStatus,
    ElectricalSpecs,
    EnvironmentSpecs,
    FreshnessStatus,
    InterfaceSpecs,
    PhysicalSpecs,
    PricingSpecs,
    VendorInfo,
    VendorListing,
)
from backend.workline.procurement.normalize import (
    PricingNormalizer,
    generate_component_id,
    normalize_manufacturer,
    normalize_mpn,
)
from backend.workline.procurement.providers.base import ProcurementProvider
from backend.workline.scraping.engine import ScraplingEngine, scraping_engine


class ScraplingProvider(ProcurementProvider):
    """
    Universal web acquisition provider for sources not indexed by Nexar,
    local Indian distributors (Robu, Robocraze), and direct manufacturer pages.
    """

    def __init__(self, engine: Optional[ScraplingEngine] = None):
        self.engine = engine or scraping_engine
        self.pricing_norm = PricingNormalizer()

    @property
    def name(self) -> str:
        return "Scrapling"

    @property
    def is_enabled(self) -> bool:
        return True

    async def search_components(
        self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[ComponentCandidate]:
        """Search local distributors and web sources using Scrapling engine."""
        from backend.workline.procurement.vendors.robu import RobuVendor
        from backend.workline.procurement.vendors.robocraze import RobocrazeVendor

        robu = RobuVendor(engine=self.engine)
        robocraze = RobocrazeVendor(engine=self.engine)

        tasks = [
            robu.search(query, limit=limit),
            robocraze.search(query, limit=limit),
        ]
        results_nested = await asyncio.gather(*tasks, return_exceptions=True)

        flat_candidates: List[ComponentCandidate] = []
        for r in results_nested:
            if isinstance(r, list):
                flat_candidates.extend(r)

        return flat_candidates[:limit]

    async def search_mpn(self, mpn: str) -> Optional[ComponentCandidate]:
        """Search specific MPN across web adapters."""
        results = await self.search_components(mpn, limit=1)
        return results[0] if results else None

    async def get_component(self, component_id: str) -> Optional[ComponentCandidate]:
        """Fetch component by canonical ID."""
        parts = component_id.replace("component:", "").split("_", 1)
        mpn_query = parts[1] if len(parts) > 1 else parts[0]
        return await self.search_mpn(mpn_query)

    async def get_offers(self, mpn: str) -> List[VendorListing]:
        """Fetch active scraped vendor listings."""
        cand = await self.search_mpn(mpn)
        return cand.listings if cand else []

    async def get_datasheets(self, mpn: str) -> List[DatasheetMetadata]:
        """Fetch discovered datasheets from scraped sources."""
        cand = await self.search_mpn(mpn)
        if cand and cand.datasheet:
            return [
                DatasheetMetadata(
                    datasheet_id=cand.datasheet.datasheet_id,
                    component_id=cand.component_id,
                    url=cand.datasheet.url,
                    source=self.name,
                    manufacturer=cand.manufacturer,
                    mpn=cand.manufacturer_part_number,
                    title=cand.datasheet.title,
                    document_type=cand.datasheet.document_type,
                    verification_status=cand.datasheet.verification_status,
                )
            ]
        return []
