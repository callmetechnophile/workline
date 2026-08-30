"""Research paper provider adapters."""

from research_agents.research_paper_agent.providers.base import BasePaperProvider
from research_agents.research_paper_agent.providers.freephdlabor import FreephdlaborProvider

__all__ = ["BasePaperProvider", "FreephdlaborProvider"]
