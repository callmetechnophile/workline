"""Engineering Knowledge and Decision Memory package."""

from backend.workline.knowledge.conflicts import (
    ConflictDetector,
    ConflictItem,
    ConflictReport,
    conflict_detector,
)
from backend.workline.knowledge.decisions import (
    DecisionService,
    DecisionValidationError,
    DecisionValidator,
    UnauthorizedApprovalError,
    decision_service,
)
from backend.workline.knowledge.findings import (
    FindingService,
    finding_service,
)
from backend.workline.knowledge.indexing import (
    COLLECTION_KNOWLEDGE,
    KnowledgeIndexer,
    knowledge_indexer,
)
from backend.workline.knowledge.lessons import (
    LessonService,
    lesson_service,
)
from backend.workline.knowledge.models import (
    Actor,
    ActorType,
    DecisionAlternative,
    DecisionCategory,
    DecisionEvidence,
    DecisionStatus,
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
    EvidenceSourceType,
    FindingSeverity,
    FindingStatus,
    KnowledgeAuditEvent,
    KnowledgeAuditEventType,
    RequirementCategory,
    RequirementPriority,
    RequirementStatus,
)
from backend.workline.knowledge.provenance import (
    EmbeddingProvenance,
    compute_content_hash,
)
from backend.workline.knowledge.requirements import (
    RequirementService,
    TraceabilityChain,
    TraceabilityEngine,
    TraceabilityStep,
    requirement_service,
    traceability_engine,
)
from backend.workline.knowledge.retrieval import (
    KnowledgeRetrievalService,
    RetrievedKnowledgeItem,
    knowledge_retrieval,
)
from backend.workline.knowledge.service import (
    KnowledgeService,
    knowledge_service,
)
from backend.workline.knowledge.summarizer import (
    KnowledgeSummarizer,
    knowledge_summarizer,
)

__all__ = [
    "Actor",
    "ActorType",
    "DecisionCategory",
    "DecisionStatus",
    "EvidenceSourceType",
    "DecisionEvidence",
    "DecisionAlternative",
    "EngineeringDecision",
    "RequirementCategory",
    "RequirementPriority",
    "RequirementStatus",
    "EngineeringRequirement",
    "FindingStatus",
    "FindingSeverity",
    "EngineeringFinding",
    "EngineeringLesson",
    "KnowledgeAuditEventType",
    "KnowledgeAuditEvent",
    "EmbeddingProvenance",
    "compute_content_hash",
    "COLLECTION_KNOWLEDGE",
    "KnowledgeIndexer",
    "knowledge_indexer",
    "ConflictItem",
    "ConflictReport",
    "ConflictDetector",
    "conflict_detector",
    "RetrievedKnowledgeItem",
    "KnowledgeRetrievalService",
    "knowledge_retrieval",
    "TraceabilityStep",
    "TraceabilityChain",
    "TraceabilityEngine",
    "traceability_engine",
    "DecisionService",
    "decision_service",
    "DecisionValidator",
    "DecisionValidationError",
    "UnauthorizedApprovalError",
    "RequirementService",
    "requirement_service",
    "FindingService",
    "finding_service",
    "LessonService",
    "lesson_service",
    "KnowledgeSummarizer",
    "knowledge_summarizer",
    "KnowledgeService",
    "knowledge_service",
]
