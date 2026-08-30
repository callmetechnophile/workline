"""Services for DeepResearchAgent (aggregation, claim extraction, cross-comparison, synthesis, markdown formatting)."""

from research_agents.deep_research_agent.services.claim_extractor import ClaimExtractor
from research_agents.deep_research_agent.services.cross_comparator import CrossSourceComparator
from research_agents.deep_research_agent.services.evidence_aggregator import EvidenceAggregator
from research_agents.deep_research_agent.services.markdown_formatter import MarkdownReportFormatter
from research_agents.deep_research_agent.services.synthesizer import DeepResearchSynthesizer, SynthesisSchema

__all__ = [
    "EvidenceAggregator",
    "ClaimExtractor",
    "CrossSourceComparator",
    "DeepResearchSynthesizer",
    "SynthesisSchema",
    "MarkdownReportFormatter",
]
