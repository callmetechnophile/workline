"""Services for WebResearchAgent (tool selection, query planning, deduplication, ranking, extraction)."""

from research_agents.web_research_agent.services.authority import AuthorityEvaluator
from research_agents.web_research_agent.services.cache import WebQueryCache
from research_agents.web_research_agent.services.classification import SourceClassifier
from research_agents.web_research_agent.services.deduplication import WebSourceDeduplicator
from research_agents.web_research_agent.services.extraction import EvidenceExtractor
from research_agents.web_research_agent.services.ranking import WebRelevanceScorer
from research_agents.web_research_agent.services.search import WebQueryPlanner
from research_agents.web_research_agent.services.tool_selector import ToolSelector

__all__ = [
    "AuthorityEvaluator",
    "WebQueryCache",
    "SourceClassifier",
    "WebSourceDeduplicator",
    "EvidenceExtractor",
    "WebRelevanceScorer",
    "WebQueryPlanner",
    "ToolSelector",
]
