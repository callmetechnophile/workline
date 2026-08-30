"""
Root alias module proxying to research_agents.web_research_agent.
Allows direct execution via `python -m web_research_agent`.
"""

from research_agents.web_research_agent import (
    ExtractedEngineeringFact,
    NormalizedWebSource,
    StructuredError,
    WebResearchAgent,
    WebResearchAgentInput,
    WebResearchAgentOutput,
    web_research_config,
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
