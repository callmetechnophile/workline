"""
ComponentPlanningAgent — Agent #7 of WorkflowGuide AI Platform.
"""

from research_agents.component_planning_agent.agent import ComponentPlanningAgent
from research_agents.component_planning_agent.config import bom_config
from research_agents.component_planning_agent.schemas import (
    BOMAssumptionItem,
    BOMItem,
    BOMSummary,
    BOMTraceabilityItem,
    BOMUnknownItem,
    BOMValidationItem,
    CompatibilityCheck,
    ComponentAlternativeItem,
    ComponentPlanningAgentInput,
    ComponentPlanningAgentOutput,
    ComponentRequirementItem,
    ProjectMeta,
    ResourceConflict,
    StructuredError,
)

__all__ = [
    "ComponentPlanningAgent",
    "ComponentPlanningAgentInput",
    "ComponentPlanningAgentOutput",
    "ProjectMeta",
    "BOMItem",
    "ComponentRequirementItem",
    "ComponentAlternativeItem",
    "CompatibilityCheck",
    "ResourceConflict",
    "BOMValidationItem",
    "BOMUnknownItem",
    "BOMAssumptionItem",
    "BOMTraceabilityItem",
    "BOMSummary",
    "StructuredError",
    "bom_config",
]
