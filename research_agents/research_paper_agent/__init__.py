"""
ResearchPaperAgent — Agent #1 of WorkflowGuide AI Platform.
"""

from research_agents.research_paper_agent.agent import ResearchPaperAgent
from research_agents.research_paper_agent.config import research_config
from research_agents.research_paper_agent.schemas import (
    NormalizedPaper,
    ResearchPaperAgentInput,
    ResearchPaperAgentOutput,
    StructuredError,
)

__all__ = [
    "ResearchPaperAgent",
    "ResearchPaperAgentInput",
    "ResearchPaperAgentOutput",
    "NormalizedPaper",
    "StructuredError",
    "research_config",
]
