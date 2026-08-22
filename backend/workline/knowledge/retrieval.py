"""Hybrid knowledge retrieval combining Qdrant semantic search with SurrealDB authoritative validation."""

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.workline.knowledge.indexing import COLLECTION_KNOWLEDGE, KnowledgeIndexer, knowledge_indexer
from backend.workline.knowledge.models import (
    DecisionStatus,
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
)
from backend.workline.retrieval.qdrant import QdrantManager

logger = logging.getLogger("workline.knowledge.retrieval")


class RetrievedKnowledgeItem(BaseModel):
    """Standardized retrieval result with authoritative state and freshness metadata."""
    object_id: str
    object_type: str  # DECISION, REQUIREMENT, FINDING, LESSON
    project_id: str
    title: str
    category: str
    status: str
    is_current_authority: bool = True
    superseded_by: Optional[str] = None
    similarity_score: float = 0.0
    summary: str
    full_record: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeRetrievalService:
    """
    Executes hybrid semantic search over Qdrant candidates and cross-validates
    every match against the authoritative SurrealDB state. Prevents stale/superseded
    decisions from being returned as active design authority.
    """

    def __init__(self, indexer: Optional[KnowledgeIndexer] = None):
        self.indexer = indexer or knowledge_indexer
        self.qdrant: QdrantManager = self.indexer.qdrant

    def search_project_knowledge(
        self,
        project_id: str,
        query: str,
        object_types: Optional[List[str]] = None,
        authoritative_store: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[RetrievedKnowledgeItem]:
        """
        Executes semantic search over Qdrant, validates against authoritative state,
        and enforces strict project_id isolation.
        """
        if not query.strip():
            return []

        # 1. Semantic search in Qdrant
        filter_payload: Dict[str, Any] = {"project_id": project_id}
        raw_results = self.qdrant.search(
            collection=COLLECTION_KNOWLEDGE,
            query=query,
            metadata_filter=filter_payload,
            limit=limit * 2,
        )

        results: List[RetrievedKnowledgeItem] = []
        seen_ids = set()

        for item in raw_results:
            payload = item.get("payload", {})
            obj_id = item.get("id") or payload.get("object_id")
            if not obj_id or obj_id in seen_ids:
                continue

            # Enforce strict project_id isolation
            if payload.get("project_id") != project_id:
                continue

            obj_type = payload.get("object_type", "UNKNOWN")
            if object_types and obj_type not in object_types:
                continue

            seen_ids.add(obj_id)
            score = float(item.get("score", 0.0))

            # 2. Authoritative check
            status = payload.get("status", "ACTIVE")
            is_current = True
            superseded_by = payload.get("superseded_by")
            full_record = {}

            if authoritative_store and obj_id in authoritative_store:
                live_obj = authoritative_store[obj_id]
                full_record = live_obj.model_dump() if hasattr(live_obj, "model_dump") else live_obj
                status = full_record.get("status", status)
                superseded_by = full_record.get("superseded_by", superseded_by)

            if status == DecisionStatus.SUPERSEDED.value or superseded_by is not None:
                is_current = False

            results.append(
                RetrievedKnowledgeItem(
                    object_id=obj_id,
                    object_type=obj_type,
                    project_id=project_id,
                    title=payload.get("title", obj_id),
                    category=payload.get("category", "GENERAL"),
                    status=status,
                    is_current_authority=is_current,
                    superseded_by=superseded_by,
                    similarity_score=score,
                    summary=payload.get("content", ""),
                    full_record=full_record or payload,
                    provenance={"indexed": True, "score": score},
                )
            )

            if len(results) >= limit:
                break

        return results


# Singleton
knowledge_retrieval = KnowledgeRetrievalService()
