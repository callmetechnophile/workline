"""Component Search and Multi-Provider Orchestration for Workline Procurement."""

import asyncio
import re
from typing import Any, Dict, List, Optional

from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.procurement.models import (
    CandidateMetadata,
    CheckStatus,
    ComponentCandidate,
    ComponentRequirement,
)
from backend.workline.procurement.normalize import ComponentNormalizer
from backend.workline.procurement.providers.base import ProcurementProvider
from backend.workline.procurement.providers.manual import ManualProvider
from backend.workline.procurement.providers.nexar import NexarProvider
from backend.workline.procurement.providers.scrapling import ScraplingProvider
from backend.workline.procurement.validate import TechnicalValidator
from backend.workline.retrieval.qdrant import (
    COLLECTION_COMPONENTS,
    COLLECTION_RESEARCH,
    QdrantManager,
    qdrant_manager,
)


class ComponentSearchEngine:
    """
    Orchestrates Nexar (Primary) + Scrapling (Fallback/Supplementary) + Qdrant semantic retrieval,
    normalizes findings into canonical ComponentCandidate models, and applies deterministic validation.
    """

    def __init__(
        self,
        nexar: Optional[NexarProvider] = None,
        scrapling: Optional[ScraplingProvider] = None,
        manual: Optional[ManualProvider] = None,
        qdrant: Optional[QdrantManager] = None,
        project_repo: Optional[ProjectRepository] = None,
        graph_repo: Optional[GraphRepository] = None,
    ):
        self.nexar = nexar or NexarProvider()
        self.scrapling = scrapling or ScraplingProvider()
        self.manual = manual or ManualProvider()
        self.qdrant = qdrant or qdrant_manager
        self.project_repo = project_repo or ProjectRepository()
        self.graph_repo = graph_repo or GraphRepository()

        self.normalizer = ComponentNormalizer()
        self.validator = TechnicalValidator()

    def is_mpn_query(self, query: str) -> bool:
        """Heuristic check whether query is an exact part number or descriptive requirement."""
        clean = query.strip()
        # If contains spaces and multiple common English words, likely descriptive
        if " " in clean and any(w in clean.lower() for w in ["regulator", "sensor", "converter", "microcontroller", "driver", "buck", "board"]):
            return False
        # If matches alphanumeric part number pattern (e.g. TPS62130, ESP32-S3, BME280)
        return bool(re.match(r'^[a-zA-Z0-9_-]{3,20}$', clean))

    async def search_vendors(
        self, query: str, limit_per_source: int = 5, requirement: Optional[ComponentRequirement] = None
    ) -> List[ComponentCandidate]:
        """
        Executes primary Nexar search and parallel Scrapling fallback/supplementary sourcing,
        normalizing and deduplicating results under canonical component identities.
        """
        is_mpn = self.is_mpn_query(query)

        # 1. Primary: Nexar search
        nexar_task = self.nexar.search_mpn(query) if is_mpn else self.nexar.search_components(query, limit=limit_per_source)

        # 2. General / Indian / Supplementary: Scrapling search
        scrapling_task = self.scrapling.search_components(query, limit=limit_per_source)

        results_nexar, results_scrapling = await asyncio.gather(
            nexar_task,
            scrapling_task,
            return_exceptions=True,
        )

        raw_candidates: List[ComponentCandidate] = []

        if isinstance(results_nexar, list):
            raw_candidates.extend(results_nexar)
        elif isinstance(results_nexar, ComponentCandidate):
            raw_candidates.append(results_nexar)

        if isinstance(results_scrapling, list):
            raw_candidates.extend(results_scrapling)

        # 3. Normalize & Deduplicate by (Manufacturer, MPN)
        normalized_candidates = self.normalizer.normalize(raw_candidates)

        # 4. Deterministic validation & scoring if requirement is provided
        ranked_candidates = self._rank_and_score_candidates(normalized_candidates, requirement)
        return ranked_candidates

    def _rank_and_score_candidates(
        self,
        candidates: List[ComponentCandidate],
        requirement: Optional[ComponentRequirement] = None,
    ) -> List[ComponentCandidate]:
        """Score and sort candidates based on deterministic compatibility, documentation quality, and cost."""
        for c in candidates:
            breakdown = {
                "compatibility": 1.0,
                "documentation": 1.0 if (c.datasheet and c.datasheet.url) else 0.5,
                "availability": 1.0 if (c.availability.in_stock or c.availability.stock) else 0.4,
                "cost": 1.0,
            }

            if requirement:
                report = self.validator.validate(c, requirement)
                if not report.is_compatible:
                    breakdown["compatibility"] = 0.0
                    c.metadata.recommendation = "INCOMPATIBLE"
                    c.metadata.reason = f"Failed constraint: {'; '.join(w for w in report.warnings) or 'Electrical mismatch'}"
                else:
                    breakdown["compatibility"] = 1.0 if report.overall_status == CheckStatus.PASS else 0.8
                    c.metadata.recommendation = "RECOMMENDED" if report.overall_status == CheckStatus.PASS else "ALTERNATIVE"
                    c.metadata.reason = "Meets hard electrical and interface constraints with verified specifications."

            total_score = (
                breakdown["compatibility"] * 0.40
                + breakdown["documentation"] * 0.25
                + breakdown["availability"] * 0.20
                + breakdown["cost"] * 0.15
            )
            c.metadata.score = round(total_score, 3)
            c.metadata.scoring_breakdown = breakdown

        # Sort: Compatible first, then highest score
        return sorted(
            candidates,
            key=lambda x: (
                1 if x.metadata.recommendation == "RECOMMENDED" else (0 if x.metadata.recommendation == "ALTERNATIVE" else -1),
                x.metadata.score,
            ),
            reverse=True,
        )

    def search_semantic(
        self, query: str, project_id: Optional[str] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Semantic search over indexed datasheets and technical documents in Qdrant."""
        filter_dict = {"project_id": project_id} if project_id else None
        return self.qdrant.search(
            collection=COLLECTION_RESEARCH,
            query=query,
            metadata_filter=filter_dict,
            limit=limit,
        )
