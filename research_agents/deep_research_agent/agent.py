"""
Agent #4: DeepResearchAgent implementation using Google ADK conventions.
Reasons over academic research, web evidence, and processed document artifacts using Amazon Bedrock
to produce an authoritative engineering synthesis report.
"""

import asyncio
import time
from typing import Dict, List, Optional
import uuid
from loguru import logger

from research_agents.deep_research_agent.providers.base import (
    ProviderError,
    ReasoningProvider,
)
from research_agents.deep_research_agent.providers.bedrock import BedrockProvider
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
from research_agents.deep_research_agent.services.claim_extractor import ClaimExtractor
from research_agents.deep_research_agent.services.cross_comparator import CrossSourceComparator
from research_agents.deep_research_agent.services.evidence_aggregator import EvidenceAggregator
from research_agents.deep_research_agent.services.markdown_formatter import MarkdownReportFormatter
from research_agents.deep_research_agent.services.synthesizer import DeepResearchSynthesizer


class DeepResearchAgent:
    """
    Google ADK-compliant Deep Research & Engineering Synthesis Agent.
    Synthesizes multi-source engineering research and evidence into actionable trade studies,
    verified claims, and architectural decisions using Amazon Bedrock.
    """

    NAME = "DeepResearchAgent"
    DESCRIPTION = (
        "Synthesizes multi-source engineering research and evidence into actionable trade studies, "
        "verified claims, and architectural decisions using Amazon Bedrock."
    )
    CAPABILITIES = [
        "research.synthesize",
        "research.trade_study",
        "research.compare",
        "research.claims",
        "research.report",
    ]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        evidence_aggregator: Optional[EvidenceAggregator] = None,
        claim_extractor: Optional[ClaimExtractor] = None,
        comparator: Optional[CrossSourceComparator] = None,
        synthesizer: Optional[DeepResearchSynthesizer] = None,
        markdown_formatter: Optional[MarkdownReportFormatter] = None,
    ):
        self.provider = reasoning_provider or BedrockProvider()
        self.evidence_aggregator = evidence_aggregator or EvidenceAggregator()
        self.claim_extractor = claim_extractor or ClaimExtractor()
        self.comparator = comparator or CrossSourceComparator()
        self.synthesizer = synthesizer or DeepResearchSynthesizer(self.provider)
        self.markdown_formatter = markdown_formatter or MarkdownReportFormatter()

    async def run(
        self,
        input_data: DeepResearchAgentInput,
        execution_id: Optional[str] = None,
    ) -> DeepResearchAgentOutput:
        """
        Executes end-to-end evidence aggregation, Bedrock reasoning, cross-source comparison,
        claim classification, and engineering synthesis report generation.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.execution_context.execution_id if input_data.execution_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        logger.info(
            f"[{exec_id}][{self.NAME}] Starting deep research synthesis for project='{input_data.project.title}' "
            f"domain='{input_data.project.engineering_domain}'"
        )

        errors: List[StructuredError] = []

        # 1. Aggregate and Validate Evidence Items
        evidence_items, agg_warnings = self.evidence_aggregator.aggregate_and_validate(input_data)
        if agg_warnings:
            for w in agg_warnings:
                logger.warning(f"[{exec_id}][{self.NAME}] Evidence notice: {w}")

        # 2. Cross-Source Pre-Analysis (Consensus & Contradictions)
        pre_comparisons, pre_contradictions = self.comparator.detect_cross_source_patterns(evidence_items)

        # 3. Amazon Bedrock Reasoning & Synthesis
        try:
            raw_synthesis = await self.synthesizer.synthesize(
                project=input_data.project,
                evidence=evidence_items,
            )
        except ProviderError as pe:
            logger.error(f"[{exec_id}][{self.NAME}] Reasoning provider error ({pe.provider}): {pe.message}")
            return DeepResearchAgentOutput(
                status="error",
                project=input_data.project,
                evidence_used=evidence_items,
                errors=[StructuredError(code=pe.code, message=pe.message, retryable=pe.retryable)],
            )
        except Exception as e:
            logger.error(f"[{exec_id}][{self.NAME}] Unexpected synthesis failure: {str(e)}")
            return DeepResearchAgentOutput(
                status="error",
                project=input_data.project,
                evidence_used=evidence_items,
                errors=[StructuredError(code="SYNTHESIS_ERROR", message=str(e), retryable=False)],
            )

        # 4. Validate & Classify Synthesized Claims
        validated_claims = self.claim_extractor.validate_claims(
            claims=raw_synthesis.extracted_claims,
            valid_evidence=evidence_items,
        )

        # 5. Merge Cross-Source Comparisons and Contradictions
        all_comparisons = pre_comparisons + [
            c for c in raw_synthesis.cross_source_comparisons
            if c.topic not in {pc.topic for pc in pre_comparisons}
        ]
        all_contradictions = pre_contradictions + [
            ct for ct in raw_synthesis.contradictions
            if ct.topic not in {pct.topic for pct in pre_contradictions}
        ]

        # 6. Format Structured Markdown Synthesis Report
        markdown_report = self.markdown_formatter.format_report(
            project=input_data.project,
            executive_summary=raw_synthesis.executive_summary,
            architecture_analysis=raw_synthesis.architecture_analysis,
            trade_studies=raw_synthesis.component_trade_studies,
            claims=validated_claims,
            comparisons=all_comparisons,
            contradictions=all_contradictions,
            implications=raw_synthesis.engineering_implications,
            recommendations=raw_synthesis.recommendations,
            research_gaps=raw_synthesis.research_gaps,
            evidence_used=evidence_items,
        )

        elapsed = time.time() - start_time
        logger.info(
            f"[{exec_id}][{self.NAME}] Completed research synthesis in {elapsed:.3f}s. "
            f"Evidence: {len(evidence_items)}, Claims: {len(validated_claims)}, "
            f"Trade Studies: {len(raw_synthesis.component_trade_studies)}, Recommendations: {len(raw_synthesis.recommendations)}"
        )

        return DeepResearchAgentOutput(
            status="success",
            project=input_data.project,
            executive_summary=raw_synthesis.executive_summary,
            architecture_analysis=raw_synthesis.architecture_analysis,
            component_trade_studies=raw_synthesis.component_trade_studies,
            extracted_claims=validated_claims,
            cross_source_comparisons=all_comparisons,
            contradictions=all_contradictions,
            engineering_implications=raw_synthesis.engineering_implications,
            recommendations=raw_synthesis.recommendations,
            research_gaps=raw_synthesis.research_gaps,
            evidence_used=evidence_items,
            structured_markdown_report=markdown_report,
            errors=errors,
        )

    def run_sync(
        self,
        input_data: DeepResearchAgentInput,
        execution_id: Optional[str] = None,
    ) -> DeepResearchAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods
    # =========================================================================

    def synthesize_research(self, input_data: DeepResearchAgentInput) -> DeepResearchAgentOutput:
        """ADK Capability: Executes end-to-end research synthesis synchronously."""
        return self.run_sync(input_data)

    def aggregate_evidence(self, input_data: DeepResearchAgentInput) -> List[EvidenceItem]:
        """ADK Capability: Normalizes and aggregates evidence across agents."""
        evidence, _ = self.evidence_aggregator.aggregate_and_validate(input_data)
        return evidence

    def extract_claims(self, claims: List[SynthesizedClaim], evidence: List[EvidenceItem]) -> List[SynthesizedClaim]:
        """ADK Capability: Classifies and validates claims with evidence IDs."""
        return self.claim_extractor.validate_claims(claims, evidence)

    def compare_sources(self, evidence: List[EvidenceItem]) -> List[CrossSourceComparison]:
        """ADK Capability: Detects consensus and divergence across sources."""
        comparisons, _ = self.comparator.detect_cross_source_patterns(evidence)
        return comparisons

    def generate_report_markdown(self, output: DeepResearchAgentOutput) -> str:
        """ADK Capability: Formats deep research output as publication-ready Markdown."""
        return self.markdown_formatter.format_report(
            project=output.project,
            executive_summary=output.executive_summary,
            architecture_analysis=output.architecture_analysis,
            trade_studies=output.component_trade_studies,
            claims=output.extracted_claims,
            comparisons=output.cross_source_comparisons,
            contradictions=output.contradictions,
            implications=output.engineering_implications,
            recommendations=output.recommendations,
            research_gaps=output.research_gaps,
            evidence_used=output.evidence_used,
        )
