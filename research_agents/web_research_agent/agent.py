"""
Agent #2: WebResearchAgent implementation using Google ADK conventions.
Coordinates query planning, tool selection (Tavily/Anakin), caching, deduplication,
classification, authority scoring, relevance ranking, and evidence fact extraction.
"""

import asyncio
from datetime import datetime
import hashlib
import time
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.web_research_agent.config import web_research_config
from research_agents.web_research_agent.providers.anakin import AnakinProvider
from research_agents.web_research_agent.providers.base import (
    ProviderError,
    WebResearchProvider,
)
from research_agents.web_research_agent.providers.tavily import TavilyProvider
from research_agents.web_research_agent.schemas import (
    ExtractedEngineeringFact,
    NormalizedWebSource,
    ProjectMeta,
    RawWebResult,
    StructuredError,
    WebResearchAgentInput,
    WebResearchAgentOutput,
)
from research_agents.web_research_agent.services.authority import AuthorityEvaluator
from research_agents.web_research_agent.services.cache import WebQueryCache
from research_agents.web_research_agent.services.classification import SourceClassifier
from research_agents.web_research_agent.services.deduplication import WebSourceDeduplicator
from research_agents.web_research_agent.services.extraction import EvidenceExtractor
from research_agents.web_research_agent.services.ranking import WebRelevanceScorer
from research_agents.web_research_agent.services.search import WebQueryPlanner
from research_agents.web_research_agent.services.tool_selector import ToolSelector


class WebResearchAgent:
    """
    Google ADK-compliant Web Research & Evidence Agent.
    Investigates public engineering repositories, manufacturer documentation, datasheets,
    and implementation tutorials using Tavily and Anakin.
    """

    NAME = "WebResearchAgent"
    DESCRIPTION = (
        "Finds, extracts, evaluates, and structures publicly available engineering information from the web."
    )
    CAPABILITIES = [
        "web.search",
        "web.extract",
        "web.crawl",
        "web.research",
        "web.source",
    ]

    def __init__(
        self,
        tavily_provider: Optional[WebResearchProvider] = None,
        anakin_provider: Optional[WebResearchProvider] = None,
        cache: Optional[WebQueryCache] = None,
        planner: Optional[WebQueryPlanner] = None,
        tool_selector: Optional[ToolSelector] = None,
        deduplicator: Optional[WebSourceDeduplicator] = None,
        classifier: Optional[SourceClassifier] = None,
        authority_evaluator: Optional[AuthorityEvaluator] = None,
        scorer: Optional[WebRelevanceScorer] = None,
        extractor: Optional[EvidenceExtractor] = None,
    ):
        self.tavily = tavily_provider or TavilyProvider()
        self.anakin = anakin_provider or AnakinProvider()
        self.cache = cache or WebQueryCache()
        self.planner = planner or WebQueryPlanner()
        self.tool_selector = tool_selector or ToolSelector()
        self.deduplicator = deduplicator or WebSourceDeduplicator()
        self.classifier = classifier or SourceClassifier()
        self.authority_evaluator = authority_evaluator or AuthorityEvaluator()
        self.scorer = scorer or WebRelevanceScorer()
        self.extractor = extractor or EvidenceExtractor()

    async def run(
        self,
        input_data: WebResearchAgentInput,
        execution_id: Optional[str] = None,
    ) -> WebResearchAgentOutput:
        """
        Executes the end-to-end web research and evidence extraction pipeline.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.request_context.execution_id if input_data.request_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        logger.info(
            f"[{exec_id}][{self.NAME}] Starting web research for project='{input_data.project_title}' "
            f"domain='{input_data.engineering_domain}' max_sources={input_data.max_sources}"
        )

        errors: List[StructuredError] = []
        all_raw_results: List[RawWebResult] = []

        # 1. Multi-Angle Query Generation
        queries = self.planner.plan_queries(input_data)
        logger.info(f"[{exec_id}][{self.NAME}] Generated {len(queries)} web search queries: {queries}")

        # 2. Query Execution & Tool Routing
        for q in queries:
            tool_choice, tool_reason = self.tool_selector.select_tool(
                task_intent="find engineering web sources",
                query=q,
            )

            # Check if query is academic
            if tool_choice == "delegate_academic":
                logger.info(f"[{exec_id}][{self.NAME}] Query '{q}' detected as academic. {tool_reason}")
                errors.append(
                    StructuredError(
                        code="DELEGATE_ACADEMIC",
                        provider="agent_orchestrator",
                        message=f"Query '{q}' is academic: delegated to Agent #1 (ResearchPaperAgent).",
                        retryable=False,
                    )
                )
                continue

            provider = self.anakin if "anakin" in tool_choice else self.tavily
            provider_name = "anakin" if "anakin" in tool_choice else "tavily"

            # Check Cache
            cached = self.cache.get(provider=provider_name, target=q)
            if cached is not None:
                logger.info(f"[{exec_id}][{self.NAME}] Cache hit for query='{q}' (count={len(cached)})")
                all_raw_results.extend(cached)
                continue

            try:
                results = await provider.search(
                    query=q,
                    limit=input_data.max_sources,
                    execution_id=exec_id,
                )
                self.cache.set(provider=provider_name, target=q, records=results)
                all_raw_results.extend(results)
            except ProviderError as pe:
                logger.warning(f"[{exec_id}][{self.NAME}] Provider error ({pe.provider}) on query='{q}': {pe.message}")
                errors.append(
                    StructuredError(
                        code=pe.code,
                        provider=pe.provider,
                        message=f"Query '{q}': {pe.message}",
                        retryable=pe.retryable,
                    )
                )
            except Exception as e:
                logger.error(f"[{exec_id}][{self.NAME}] Unexpected error on query='{q}': {str(e)}")
                errors.append(
                    StructuredError(
                        code="INTERNAL_SEARCH_ERROR",
                        provider=provider_name,
                        message=f"Query '{q}': {str(e)}",
                        retryable=False,
                    )
                )

        sources_found = len(all_raw_results)

        # 3. Deterministic Deduplication
        unique_results = self.deduplicator.deduplicate(all_raw_results)
        logger.info(
            f"[{exec_id}][{self.NAME}] Deduplicated {sources_found} raw sources -> {len(unique_results)} unique"
        )

        # 4. Classification, Authority Evaluation, and Relevance Scoring
        normalized_sources: List[NormalizedWebSource] = []
        for raw in unique_results:
            source_type, domain = self.classifier.classify(raw)
            authority_score, authority_reasons = self.authority_evaluator.evaluate_authority(source_type, domain)
            relevance_score, relevance_reasons = self.scorer.score_source(raw, input_data)

            # Generate stable source_id
            source_id = f"src_{hashlib.md5(raw.url.encode('utf-8')).hexdigest()[:10]}"

            normalized = NormalizedWebSource(
                source_id=source_id,
                title=raw.title.strip(),
                url=raw.url.strip(),
                domain=domain,
                source_type=source_type,
                publisher=raw.publisher or domain,
                author=raw.author,
                published_date=raw.published_date,
                description=raw.snippet or (raw.content[:250] if raw.content else None),
                extracted_content=raw.content,
                relevance_score=relevance_score,
                relevance_reasons=relevance_reasons,
                authority_score=authority_score,
                authority_reasons=authority_reasons,
                source_tool=raw.source_tool,
                accessed_at=datetime.utcnow().isoformat(),
                content_available=bool(raw.content or raw.snippet),
            )
            normalized_sources.append(normalized)

        # Sort by composite rank: relevance_score * 0.7 + authority_score * 0.3
        normalized_sources.sort(
            key=lambda s: (s.relevance_score * 0.70 + s.authority_score * 0.30),
            reverse=True,
        )

        # 5. Apply Max Sources Cap
        target_limit = min(input_data.max_sources, web_research_config.max_sources_cap)
        selected_sources = normalized_sources[:target_limit]

        # 6. Extract Structured Engineering Facts with Strict Provenance
        all_facts: List[ExtractedEngineeringFact] = []
        for src in selected_sources:
            extracted_facts = self.extractor.extract_facts(
                source=src,
                components_filter=input_data.components,
            )
            all_facts.extend(extracted_facts)

        elapsed = time.time() - start_time
        status = "success" if (selected_sources or not errors) else "error"

        logger.info(
            f"[{exec_id}][{self.NAME}] Completed web research in {elapsed:.3f}s. "
            f"Found: {sources_found}, Selected: {len(selected_sources)}, Facts: {len(all_facts)}, Errors: {len(errors)}"
        )

        return WebResearchAgentOutput(
            status=status,
            project=ProjectMeta(
                title=input_data.project_title,
                domain=input_data.engineering_domain,
            ),
            queries_used=queries,
            sources_found=sources_found,
            sources_selected=len(selected_sources),
            sources=selected_sources,
            facts=all_facts,
            errors=errors,
        )

    def run_sync(
        self,
        input_data: WebResearchAgentInput,
        execution_id: Optional[str] = None,
    ) -> WebResearchAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))
