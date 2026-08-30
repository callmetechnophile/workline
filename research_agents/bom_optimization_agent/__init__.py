"""
BOMOptimizationAgent — Agent #8 of WorkflowGuide AI Platform.
"""

from research_agents.bom_optimization_agent.agent import BOMOptimizationAgent
from research_agents.bom_optimization_agent.config import opt_config
from research_agents.bom_optimization_agent.schemas import (
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
