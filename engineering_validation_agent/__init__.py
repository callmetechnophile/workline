"""
Root alias module proxying to research_agents.engineering_validation_agent.
Allows direct execution via `python -m engineering_validation_agent`.
"""

from research_agents.engineering_validation_agent import (
    EngineeringValidationAgent,
    EngineeringValidationAgentInput,
    EngineeringValidationAgentOutput,
    FinalVerdict,
    RequirementValidationItem,
    RequiredCorrection,
    StructuredError,
    ValidationItem,
    ValidationSeverityLiteral,
    ValidationStatusLiteral,
    ValidationTraceabilityItem,
    VerdictLiteral,
    val_config,
)

__all__ = [
    "EngineeringValidationAgent",
    "EngineeringValidationAgentInput",
    "EngineeringValidationAgentOutput",
    "ValidationItem",
    "RequirementValidationItem",
    "RequiredCorrection",
    "FinalVerdict",
    "ValidationTraceabilityItem",
    "StructuredError",
    "ValidationStatusLiteral",
    "ValidationSeverityLiteral",
    "VerdictLiteral",
    "val_config",
]
