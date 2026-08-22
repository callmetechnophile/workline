"""Knowledge Graph module exports."""

from backend.workline.knowledge.graph.models import (
    CanonicalEntity,
    EngineeringRelationship,
    EntityMention,
    EntityStatus,
    EntityType,
    RelationshipType,
    Specification,
    SpecificationConflict,
)
from backend.workline.knowledge.graph.normalizer import EntityNormalizer, NormalizedQuantity
from backend.workline.knowledge.graph.resolver import EntityResolver, ResolutionResult
from backend.workline.knowledge.graph.service import KnowledgeGraphService, knowledge_graph_service

__all__ = [
    "CanonicalEntity",
    "EngineeringRelationship",
    "EntityMention",
    "EntityStatus",
    "EntityType",
    "RelationshipType",
    "Specification",
    "SpecificationConflict",
    "EntityNormalizer",
    "NormalizedQuantity",
    "EntityResolver",
    "ResolutionResult",
    "KnowledgeGraphService",
    "knowledge_graph_service",
]
