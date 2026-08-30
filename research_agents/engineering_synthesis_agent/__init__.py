"""
EngineeringSynthesisAgent — Agent #5 of WorkflowGuide AI Platform.
"""

from research_agents.engineering_synthesis_agent.agent import EngineeringSynthesisAgent
from research_agents.engineering_synthesis_agent.config import eng_config
from research_agents.engineering_synthesis_agent.schemas import (
    AssumptionItem,
    DecisionTraceability,
    EngineeringDecision,
    EngineeringRisk,
    EngineeringSynthesisAgentInput,
    EngineeringSynthesisAgentOutput,
    EngineeringTradeoff,
    ExperimentPlan,
    ProjectMeta,
    RecommendationItem,
    RequirementAnalysis,
    StructuredError,
    TechnicalFinding,
    UnknownItem,
    ValidationRequirement,
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
    "StructuredError",
    "eng_config",
]
