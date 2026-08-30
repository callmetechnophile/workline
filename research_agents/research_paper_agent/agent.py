"""
Agent #1: ResearchPaperAgent implementation using Google ADK conventions.
Coordinates query planning, Freephdlabor acquisition, deduplication, and ranking.
"""

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.research_paper_agent.config import research_config
from research_agents.research_paper_agent.providers.base import (
    BasePaperProvider,
    ProviderError,
)
from research_agents.research_paper_agent.providers.freephdlabor import FreephdlaborProvider
from research_agents.research_paper_agent.schemas import (
    NormalizedPaper,
    ProjectMeta,
    RawPaperRecord,
    ResearchPaperAgentInput,
    ResearchPaperAgentOutput,
    StructuredError,
)
from research_agents.research_paper_agent.services.cache import QueryCache
from research_agents.research_paper_agent.services.deduplication import PaperDeduplicator
from research_agents.research_paper_agent.services.ranking import RelevanceScorer
from research_agents.research_paper_agent.services.retrieval import PaperNormalizer
from research_agents.research_paper_agent.services.search import QueryPlanner


class ResearchPaperAgent:
    """
    Google ADK-compliant Research Paper Acquisition Agent.
    Discovers, collects, deduplicates, and ranks academic research papers via Freephdlabor.
    """

    NAME = "ResearchPaperAgent"
    DESCRIPTION = (
        "Discovers and retrieves engineering research papers relevant to a "
        "supplied project context using Freephdlabor."
    )
    CAPABILITIES = ["research.search", "research.retrieve", "research.list"]

    def __init__(
        self,
        provider: Optional[BasePaperProvider] = None,
        cache: Optional[QueryCache] = None,
        planner: Optional[QueryPlanner] = None,
        deduplicator: Optional[PaperDeduplicator] = None,
        scorer: Optional[RelevanceScorer] = None,
    ):
        self.provider = provider or FreephdlaborProvider()
        self.cache = cache or QueryCache()
        self.planner = planner or QueryPlanner()
        self.deduplicator = deduplicator or PaperDeduplicator()
        self.scorer = scorer or RelevanceScorer()

    async def run(
        self,
        input_data: ResearchPaperAgentInput,
        execution_id: Optional[str] = None,
    ) -> ResearchPaperAgentOutput:
        """
        Executes the end-to-end academic paper acquisition workflow.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.request_context.execution_id if input_data.request_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        logger.info(
            f"[{exec_id}][{self.NAME}] Starting paper acquisition for project='{input_data.project_title}' "
            f"domain='{input_data.engineering_domain}' max_papers={input_data.max_papers}"
        )

        errors: List[StructuredError] = []
        all_raw_papers: List[RawPaperRecord] = []

        # 1. Multi-Query Planning
        queries = self.planner.plan_queries(input_data)
        logger.info(f"[{exec_id}][{self.NAME}] Generated {len(queries)} focused search queries: {queries}")

        # 2. Freephdlabor Search Execution (with Cache)
        for q in queries:
            cached = self.cache.get(provider="freephdlabor", query=q)
            if cached is not None:
                logger.info(f"[{exec_id}][{self.NAME}] Cache hit for query='{q}' (count={len(cached)})")
                all_raw_papers.extend(cached)
                continue

            try:
                results = await self.provider.search(
                    query=q,
                    limit=input_data.max_papers,
                    execution_id=exec_id,
                )
                self.cache.set(provider="freephdlabor", query=q, records=results)
                all_raw_papers.extend(results)
            except ProviderError as pe:
                logger.warning(f"[{exec_id}][{self.NAME}] Provider error on query='{q}': {pe.message}")
                errors.append(
                    StructuredError(
                        code=pe.code,
                        message=f"Query '{q}': {pe.message}",
                        retryable=pe.retryable,
                    )
                )
            except Exception as e:
                logger.error(f"[{exec_id}][{self.NAME}] Unexpected error on query='{q}': {str(e)}")
                errors.append(
                    StructuredError(
                        code="INTERNAL_SEARCH_ERROR",
                        message=f"Query '{q}': {str(e)}",
                        retryable=False,
                    )
                )

        papers_found = len(all_raw_papers)

        # 3. Deterministic Deduplication
        unique_raw = self.deduplicator.deduplicate(all_raw_papers)
        logger.info(
            f"[{exec_id}][{self.NAME}] Deduplicated {papers_found} candidates -> {len(unique_raw)} unique papers"
        )

        # 4. Relevance Ranking & Reason Generation
        scored_papers: List[NormalizedPaper] = []
        for raw in unique_raw:
            score, reasons = self.scorer.score_paper(raw, input_data)
            normalized = PaperNormalizer.normalize(
                raw=raw,
                relevance_score=score,
                relevance_reasons=reasons,
            )
            scored_papers.append(normalized)

        # Sort by relevance_score descending
        scored_papers.sort(key=lambda p: p.relevance_score, reverse=True)

        # 5. Apply Requested Limits (capped between 1 and 50)
        target_limit = min(input_data.max_papers, research_config.max_papers_cap)
        selected_papers = scored_papers[:target_limit]

        elapsed = time.time() - start_time
        status = "success" if (selected_papers or not errors) else "error"

        logger.info(
            f"[{exec_id}][{self.NAME}] Finished acquisition in {elapsed:.3f}s. "
            f"Found: {papers_found}, Selected: {len(selected_papers)}, Errors: {len(errors)}"
        )

        return ResearchPaperAgentOutput(
            status=status,
            project=ProjectMeta(
                title=input_data.project_title,
                domain=input_data.engineering_domain,
            ),
            queries_used=queries,
            papers_found=papers_found,
            papers_selected=len(selected_papers),
            papers=selected_papers,
            errors=errors,
        )

    def run_sync(
        self,
        input_data: ResearchPaperAgentInput,
        execution_id: Optional[str] = None,
    ) -> ResearchPaperAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))
