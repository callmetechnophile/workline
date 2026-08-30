"""
Repository interface for BOMOptimizationAgent supplier offers, orders, shipping options, and strategies.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback (Section 41).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.bom_optimization_agent.schemas import (
    BOMOptimizationAgentOutput,
    ProcurementStrategy,
    ShippingOption,
    SupplierOffer,
    SupplierOrder,
)


class ProcurementOptimizationRepository(ABC):
    """Abstract persistence interface for procurement plans and supplier datasets."""

    @abstractmethod
    async def save_optimization(self, output: BOMOptimizationAgentOutput) -> str:
        """Persists full procurement optimization model."""
        pass

    @abstractmethod
    async def save_supplier_offer(self, offer: SupplierOffer, project_id: str) -> str:
        """Persists single supplier pricing/availability offer."""
        pass

    @abstractmethod
    async def save_shipping_option(self, ship: ShippingOption, project_id: str) -> str:
        """Persists carrier shipping quote/estimate."""
        pass

    @abstractmethod
    async def save_order(self, order: SupplierOrder, project_id: str) -> str:
        """Persists consolidated supplier order."""
        pass

    @abstractmethod
    async def save_strategy(self, strategy: ProcurementStrategy, project_id: str) -> str:
        """Persists procurement strategy configuration."""
        pass

    @abstractmethod
    async def save_procurement_warning(self, warning: str, project_id: str) -> str:
        """Persists procurement warning item."""
        pass

    @abstractmethod
    async def get_optimization(self, project_id: str) -> Optional[BOMOptimizationAgentOutput]:
        """Retrieves procurement optimization by project ID."""
        pass


class InMemoryProcurementOptimizationRepository(ProcurementOptimizationRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._optimizations: Dict[str, BOMOptimizationAgentOutput] = {}
        self._offers: Dict[str, List[SupplierOffer]] = {}
        self._shipping_options: Dict[str, List[ShippingOption]] = {}
        self._orders: Dict[str, List[SupplierOrder]] = {}
        self._strategies: Dict[str, List[ProcurementStrategy]] = {}
        self._warnings: Dict[str, List[str]] = {}

    async def save_optimization(self, output: BOMOptimizationAgentOutput) -> str:
        proj_id = output.project_id or output.optimization_id
        self._optimizations[proj_id] = output
        return proj_id

    async def save_supplier_offer(self, offer: SupplierOffer, project_id: str) -> str:
        if project_id not in self._offers:
            self._offers[project_id] = []
        self._offers[project_id].append(offer)
        return f"{project_id}_{offer.supplier_id}_{offer.bom_item_id}"

    async def save_shipping_option(self, ship: ShippingOption, project_id: str) -> str:
        if project_id not in self._shipping_options:
            self._shipping_options[project_id] = []
        self._shipping_options[project_id].append(ship)
        return f"{project_id}_{ship.shipping_id}"

    async def save_order(self, order: SupplierOrder, project_id: str) -> str:
        if project_id not in self._orders:
            self._orders[project_id] = []
        self._orders[project_id].append(order)
        return f"{project_id}_{order.order_id}"

    async def save_strategy(self, strategy: ProcurementStrategy, project_id: str) -> str:
        if project_id not in self._strategies:
            self._strategies[project_id] = []
        self._strategies[project_id].append(strategy)
        return f"{project_id}_{strategy.strategy_id}"

    async def save_procurement_warning(self, warning: str, project_id: str) -> str:
        if project_id not in self._warnings:
            self._warnings[project_id] = []
        self._warnings[project_id].append(warning)
        return f"{project_id}_warn_{len(self._warnings[project_id])}"

    async def get_optimization(self, project_id: str) -> Optional[BOMOptimizationAgentOutput]:
        return self._optimizations.get(project_id)
