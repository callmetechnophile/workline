"""Base Procurement Provider interface for Workline."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.workline.procurement.models import (
    ComponentCandidate,
    DatasheetMetadata,
    VendorListing,
)


class ProcurementProvider(ABC):
    """Abstract interface defining required capabilities for any component intelligence provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier name."""
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if provider is configured and available."""
        pass

    @abstractmethod
    async def search_components(
        self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[ComponentCandidate]:
        """Search structured component database by keyword or specifications."""
        pass

    @abstractmethod
    async def search_mpn(self, mpn: str) -> Optional[ComponentCandidate]:
        """Exact search for a specific Manufacturer Part Number."""
        pass

    @abstractmethod
    async def get_component(self, component_id: str) -> Optional[ComponentCandidate]:
        """Fetch full details and specifications for a component ID."""
        pass

    @abstractmethod
    async def get_offers(self, mpn: str) -> List[VendorListing]:
        """Fetch live distributor pricing, stock, lead time, and MOQ offers."""
        pass

    @abstractmethod
    async def get_datasheets(self, mpn: str) -> List[DatasheetMetadata]:
        """Discover official technical datasheets, guidelines, and reference manuals."""
        pass
