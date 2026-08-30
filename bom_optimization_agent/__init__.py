"""
Root alias module proxying to research_agents.bom_optimization_agent.
Allows direct execution via `python -m bom_optimization_agent`.
"""

from research_agents.bom_optimization_agent import (
    BOMOptimizationAgent,
    BOMOptimizationAgentInput,
    BOMOptimizationAgentOutput,
    CostSummary,
    Location,
    OptimizedBOMItem,
    OrderItem,
    ProcurementStrategy,
    ProcurementTraceabilityItem,
    ProjectConstraints,
    ProjectMeta,
    ShippingOption,
    StructuredError,
    SupplierOffer,
    SupplierOrder,
    opt_config,
)

__all__ = [
    "BOMOptimizationAgent",
    "BOMOptimizationAgentInput",
    "BOMOptimizationAgentOutput",
    "ProjectMeta",
    "ProjectConstraints",
    "Location",
    "SupplierOffer",
    "ShippingOption",
    "OrderItem",
    "SupplierOrder",
    "OptimizedBOMItem",
    "ProcurementStrategy",
    "CostSummary",
    "ProcurementTraceabilityItem",
    "StructuredError",
    "opt_config",
]
