"""
DeepResearchAgent — Agent #4 of WorkflowGuide AI Platform.
"""

from research_agents.deep_research_agent.agent import DeepResearchAgent
from research_agents.deep_research_agent.config import deep_research_config
from research_agents.deep_research_agent.schemas import (
    ComponentTradeStudy,
    ContradictionReport,
    CrossSourceComparison,
    DeepResearchAgentInput,
    DeepResearchAgentOutput,
    EngineeringImplication,
    EngineeringRecommendation,
    EvidenceItem,
    ProjectMeta,
    StructuredError,
    SynthesizedClaim,
)

__all__ = [
    "DeepResearchAgent",
    "DeepResearchAgentInput",
    "DeepResearchAgentOutput",
    "ProjectMeta",
    "EvidenceItem",
    "SynthesizedClaim",
    "ComponentTradeStudy",
    "CrossSourceComparison",
    "ContradictionReport",
    "EngineeringImplication",
    "EngineeringRecommendation",
    "StructuredError",
    "deep_research_config",
]
