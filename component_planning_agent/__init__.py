"""
Root alias module proxying to research_agents.component_planning_agent.
Allows direct execution via `python -m component_planning_agent`.
"""

from research_agents.component_planning_agent import (
    BOMAssumptionItem,
    BOMItem,
    BOMSummary,
    BOMTraceabilityItem,
    BOMUnknownItem,
    BOMValidationItem,
    CompatibilityCheck,
    ComponentAlternativeItem,
    ComponentPlanningAgent,
    ComponentPlanningAgentInput,
    ComponentPlanningAgentOutput,
    ComponentRequirementItem,
    ProjectMeta,
    ResourceConflict,
    StructuredError,
    bom_config,
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
