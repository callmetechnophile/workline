"""
Root alias module proxying to research_agents.engineering_synthesis_agent.
Allows direct execution via `python -m engineering_synthesis_agent`.
"""

from research_agents.engineering_synthesis_agent import (
    AssumptionItem,
    DecisionTraceability,
    EngineeringDecision,
    EngineeringRisk,
    EngineeringSynthesisAgent,
    EngineeringSynthesisAgentInput,
    EngineeringSynthesisAgentOutput,
    EngineeringTradeoff,
    ExperimentPlan,
    ProjectMeta,
    RecommendationItem,
    RequirementAnalysis,
    TechnicalFinding,
    UnknownItem,
    ValidationRequirement,
    eng_config,
)

__all__ = [
    "EngineeringSynthesisAgent",
    "EngineeringSynthesisAgentInput",
    "EngineeringSynthesisAgentOutput",
    "ProjectMeta",
    "RequirementAnalysis",
    "TechnicalFinding",
    "EngineeringTradeoff",
    "EngineeringDecision",
    "RecommendationItem",
    "AssumptionItem",
    "UnknownItem",
    "EngineeringRisk",
    "ValidationRequirement",
    "ExperimentPlan",
    "DecisionTraceability",
    "eng_config",
]
