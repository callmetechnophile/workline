"""
Root alias module proxying to research_agents.deep_research_agent.
Allows direct execution via `python -m deep_research_agent`.
"""

from research_agents.deep_research_agent import (
    ComponentTradeStudy,
    ContradictionReport,
    CrossSourceComparison,
    DeepResearchAgent,
    DeepResearchAgentInput,
    DeepResearchAgentOutput,
    EngineeringImplication,
    EngineeringRecommendation,
    EvidenceItem,
    ProjectMeta,
    SynthesizedClaim,
    deep_research_config,
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
    "deep_research_config",
]
