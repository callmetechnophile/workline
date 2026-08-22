"""Manual / Offline Fallback Provider for Workline Procurement."""

from typing import Any, Dict, List, Optional
from backend.workline.procurement.models import (
    ComponentCandidate,
    DatasheetMetadata,
    VendorListing,
)
from backend.workline.procurement.providers.base import ProcurementProvider


class ManualProvider(ProcurementProvider):
    """Fallback provider for engineer-provided manual component specifications."""

    def __init__(self):
        self._catalog: Dict[str, ComponentCandidate] = {}

    @property
    def name(self) -> str:
        return "Manual"

    @property
    def is_enabled(self) -> bool:
        return True

    def register_component(self, candidate: ComponentCandidate) -> None:
        """Register engineer-defined component specifications."""
        self._catalog[candidate.component_id] = candidate
        self._catalog[candidate.manufacturer_part_number.upper()] = candidate

    async def search_components(
        self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[ComponentCandidate]:
        q = query.lower()
        matches = [
            c for c in self._catalog.values()
            if q in c.manufacturer_part_number.lower() or q in (c.product_name or "").lower() or q in (c.description or "").lower()
        ]
        return list({c.component_id: c for c in matches}.values())[:limit]

    async def search_mpn(self, mpn: str) -> Optional[ComponentCandidate]:
        return self._catalog.get(mpn.upper()) or self._catalog.get(mpn)

    async def get_component(self, component_id: str) -> Optional[ComponentCandidate]:
        return self._catalog.get(component_id)

    async def get_offers(self, mpn: str) -> List[VendorListing]:
        cand = await self.search_mpn(mpn)
        return cand.listings if cand else []

    async def get_datasheets(self, mpn: str) -> List[DatasheetMetadata]:
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
