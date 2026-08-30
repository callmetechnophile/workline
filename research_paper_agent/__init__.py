"""
Root alias module proxying to research_agents.research_paper_agent.
Allows direct execution via `python -m research_paper_agent`.
"""

from research_agents.research_paper_agent import (
    NormalizedPaper,
    ResearchPaperAgent,
    ResearchPaperAgentInput,
    ResearchPaperAgentOutput,
    StructuredError,
    research_config,
)

__all__ = [
    "ResearchPaperAgent",
    "ResearchPaperAgentInput",
    "ResearchPaperAgentOutput",
    "NormalizedPaper",
    "StructuredError",
    "research_config",
]
