"""Knowledge vector indexing with provenance and incremental hash verification."""

import logging
from typing import Any, Dict, List, Optional
from backend.workline.knowledge.models import (
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
)
from backend.workline.knowledge.provenance import EmbeddingProvenance, compute_content_hash
from backend.workline.retrieval.qdrant import QdrantManager

logger = logging.getLogger("workline.knowledge.indexing")

COLLECTION_KNOWLEDGE = "workline_knowledge"


class KnowledgeIndexer:
    """
    Manages vector embeddings for engineering knowledge in Qdrant with
    incremental source hash checks to avoid unnecessary re-embedding.
    """

    def __init__(self, qdrant: Optional[QdrantManager] = None):
        self.qdrant = qdrant or QdrantManager()
        self._provenance_store: Dict[str, EmbeddingProvenance] = {}  # object_id -> EmbeddingProvenance

    def index_decision(self, decision: EngineeringDecision) -> bool:
        """Indexes decision rationale, problem statement, and selected option into Qdrant."""
        alt_text = " ".join([f"{a.name}: {a.description} (rejected: {a.rejection_reason})" for a in decision.alternatives])
        ev_text = " ".join([f"{e.title}: {e.claim}" for e in decision.evidence])
        content = (
            f"Decision: {decision.title}. "
            f"Problem: {decision.problem}. "
            f"Selected: {decision.selected_option}. "
            f"Rationale: {decision.rationale}. "
            f"Constraints: {', '.join(decision.constraints)}. "
            f"Alternatives: {alt_text}. "
            f"Evidence: {ev_text}"
        )

        content_hash = compute_content_hash(content)
        existing_prov = self._provenance_store.get(decision.decision_id)
        if existing_prov and existing_prov.source_hash == content_hash:
            # Skip re-embedding if content has not changed
            return False

        payload = {
            "project_id": decision.project_id,
            "object_type": "DECISION",
            "object_id": decision.decision_id,
            "category": decision.category.value,
            "status": decision.status.value,
            "selected_option": decision.selected_option,
            "created_at": decision.created_at,
            "superseded_by": decision.superseded_by,
            "title": decision.title,
            "content": content,
        }

        # Index in Qdrant
        self.qdrant.index_document(
            collection=COLLECTION_KNOWLEDGE,
            doc_id=decision.decision_id,
            text=content,
            payload=payload,
        )

        self._provenance_store[decision.decision_id] = EmbeddingProvenance(
            object_id=decision.decision_id,
            object_type="DECISION",
            project_id=decision.project_id,
            source_hash=content_hash,
            metadata={"status": decision.status.value},
        )
        return True

    def index_requirement(self, req: EngineeringRequirement) -> bool:
        """Indexes requirement specification into Qdrant."""
        content = f"Requirement: {req.title}. Category: {req.category.value}. Value: {req.value or ''} {req.unit or ''}. Description: {req.description}"
        content_hash = compute_content_hash(content)

        existing_prov = self._provenance_store.get(req.requirement_id)
        if existing_prov and existing_prov.source_hash == content_hash:
            return False

        payload = {
            "project_id": req.project_id,
            "object_type": "REQUIREMENT",
            "object_id": req.requirement_id,
            "category": req.category.value,
            "status": req.status.value,
            "priority": req.priority.value,
            "created_at": req.created_at,
            "title": req.title,
            "content": content,
        }

        self.qdrant.index_document(
            collection=COLLECTION_KNOWLEDGE,
            doc_id=req.requirement_id,
            text=content,
            payload=payload,
        )

        self._provenance_store[req.requirement_id] = EmbeddingProvenance(
            object_id=req.requirement_id,
            object_type="REQUIREMENT",
            project_id=req.project_id,
            source_hash=content_hash,
            metadata={"status": req.status.value},
        )
        return True

    def index_finding(self, finding: EngineeringFinding) -> bool:
        """Indexes engineering finding into Qdrant."""
        content = f"Finding: {finding.title}. Category: {finding.category}. Severity: {finding.severity.value}. Description: {finding.description}. Resolution: {finding.resolution or 'OPEN'}"
        content_hash = compute_content_hash(content)

        existing_prov = self._provenance_store.get(finding.finding_id)
        if existing_prov and existing_prov.source_hash == content_hash:
            return False

        payload = {
            "project_id": finding.project_id,
            "object_type": "FINDING",
            "object_id": finding.finding_id,
            "category": finding.category,
            "status": finding.status.value,
            "severity": finding.severity.value,
            "created_at": finding.created_at,
            "title": finding.title,
            "content": content,
        }

        self.qdrant.index_document(
            collection=COLLECTION_KNOWLEDGE,
            doc_id=finding.finding_id,
            text=content,
            payload=payload,
        )

        self._provenance_store[finding.finding_id] = EmbeddingProvenance(
            object_id=finding.finding_id,
            object_type="FINDING",
            project_id=finding.project_id,
            source_hash=content_hash,
            metadata={"status": finding.status.value},
        )
        return True

    def index_lesson(self, lesson: EngineeringLesson) -> bool:
        """Indexes engineering lesson learned into Qdrant."""
        content = (
            f"Lesson Learned: {lesson.title}. "
            f"Context: {lesson.context}. "
            f"Cause: {lesson.cause}. "
            f"Impact: {lesson.impact}. "
            f"Recommendation: {lesson.recommendation}"
        )
        content_hash = compute_content_hash(content)

        existing_prov = self._provenance_store.get(lesson.lesson_id)
        if existing_prov and existing_prov.source_hash == content_hash:
            return False

        payload = {
            "project_id": lesson.project_id,
            "object_type": "LESSON",
            "object_id": lesson.lesson_id,
            "category": "LESSON",
            "created_at": lesson.created_at,
            "title": lesson.title,
            "content": content,
        }

        self.qdrant.index_document(
            collection=COLLECTION_KNOWLEDGE,
            doc_id=lesson.lesson_id,
            text=content,
            payload=payload,
        )

        self._provenance_store[lesson.lesson_id] = EmbeddingProvenance(
            object_id=lesson.lesson_id,
            object_type="LESSON",
            project_id=lesson.project_id,
            source_hash=content_hash,
        )
        return True


# Singleton
knowledge_indexer = KnowledgeIndexer()
