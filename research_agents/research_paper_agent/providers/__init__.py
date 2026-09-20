"""Research paper provider adapters."""

from research_agents.research_paper_agent.providers.base import BasePaperProvider
from research_agents.research_paper_agent.providers.arxiv import ArxivProvider
from research_agents.research_paper_agent.providers.freephdlabor import FreephdlaborProvider

__all__ = ["BasePaperProvider", "ArxivProvider", "FreephdlaborProvider"]

