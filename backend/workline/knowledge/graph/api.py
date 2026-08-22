"""FastAPI routes for Entity and Knowledge Graph operations."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.workline.knowledge.graph.models import (
    CanonicalEntity,
    EntityMention,
    EntityType,
    Specification,
    SpecificationConflict,
)
from backend.workline.knowledge.graph.resolver import EntityResolver
from backend.workline.knowledge.graph.service import knowledge_graph_service

router = APIRouter(tags=["Knowledge Graph"])


class ResolveMentionRequest(BaseModel):
    mention: EntityMention
    manufacturer_context: Optional[str] = None


@router.get("/api/entities/search", response_model=List[CanonicalEntity])
def search_entities(
    q: str = Query(..., description="Search query"),
    project_id: Optional[str] = None,
    entity_type: Optional[EntityType] = None,
) -> List[CanonicalEntity]:
    return knowledge_graph_service.search_entities(q, project_id, entity_type)


@router.get("/api/entities/{entity_id}", response_model=CanonicalEntity)
def get_entity(entity_id: str) -> CanonicalEntity:
    ent = knowledge_graph_service.get_entity(entity_id)
    if not ent:
        raise HTTPException(status_code=404, detail="Entity not found")
    return ent


@router.get("/api/entities/{entity_id}/relationships")
def get_entity_relationships(entity_id: str) -> List[Dict[str, Any]]:
    graph_data = knowledge_graph_service.get_related(entity_id)
    if not graph_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    return graph_data.get("relationships", [])


@router.get("/api/entities/{entity_id}/specifications", response_model=List[Specification])
def get_entity_specifications(entity_id: str) -> List[Specification]:
    return knowledge_graph_service.get_specifications(entity_id)


@router.get("/api/entities/{entity_id}/conflicts", response_model=List[SpecificationConflict])
def get_entity_conflicts(entity_id: str) -> List[SpecificationConflict]:
    conflicts = knowledge_graph_service.list_conflicts()
    return [c for c in conflicts if c.entity_id == entity_id]


@router.get("/api/entities/{entity_id}/evidence")
def get_entity_evidence(entity_id: str) -> List[Dict[str, Any]]:
    specs = knowledge_graph_service.get_specifications(entity_id)
    evidence_list = []
    for s in specs:
        evidence_list.append({
            "property": s.property,
            "value": s.value,
            "document": s.source_document,
            "page": s.page,
            "section": s.section,
            "confidence": s.confidence,
        })
    return evidence_list


@router.post("/api/entities/{mention_id}/resolve")
def resolve_entity_mention(mention_id: str, req: ResolveMentionRequest) -> Dict[str, Any]:
    existing = knowledge_graph_service.search_entities("")
    result = EntityResolver.resolve_mention(
        mention=req.mention,
        existing_entities=existing,
        manufacturer_context=req.manufacturer_context,
    )
    return {
        "mention_id": mention_id,
        "status": result.status,
        "canonical_entity_id": result.canonical_entity_id,
        "confidence": result.confidence,
        "strategy": result.strategy,
        "reason": result.reason,
    }


@router.get("/api/graph/related/{entity_id}")
def get_graph_related(entity_id: str, depth: int = 2) -> Dict[str, Any]:
    res = knowledge_graph_service.get_related(entity_id, max_depth=depth)
    if not res:
        raise HTTPException(status_code=404, detail="Entity not found")
    return res
