"""
Supplier adapter abstract base class for BOMOptimizationAgent (Sections 6 & 7).
Decouples external distributor API / dataset integration from optimization algorithms.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from research_agents.bom_optimization_agent.schemas import Location, SupplierOffer


class SupplierAdapter(ABC):
    """Abstract interface for component distributors and electronic suppliers."""

    @property
    @abstractmethod
    def supplier_id(self) -> str:
        """Unique supplier identifier."""
        pass

    @property
    @abstractmethod
    def supplier_name(self) -> str:
        """Human-readable supplier name."""
        pass

    @abstractmethod
    def get_supplier_location(self) -> Location:
        """Returns supplier warehouse origin location."""
        pass

    @abstractmethod
    async def get_offers_for_bom_item(
        self,
        bom_item_id: str,
        part_number: str,
        category: str,
        quantity: int,
    ) -> List[SupplierOffer]:
        """Queries supplier availability, unit pricing, MOQs, and lead times for a BOM item."""
        pass
