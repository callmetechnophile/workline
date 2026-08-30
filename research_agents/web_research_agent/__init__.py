"""
WebResearchAgent — Agent #2 of WorkflowGuide AI Platform.
"""

from research_agents.web_research_agent.agent import WebResearchAgent
from research_agents.web_research_agent.config import web_research_config
from research_agents.web_research_agent.schemas import (
    ExtractedEngineeringFact,
    NormalizedWebSource,
    StructuredError,
    WebResearchAgentInput,
    WebResearchAgentOutput,
)

__all__ = [
    "WebResearchAgent",
    "WebResearchAgentInput",
    "WebResearchAgentOutput",
    "NormalizedWebSource",
    "ExtractedEngineeringFact",
    "StructuredError",
    "web_research_config",
]
