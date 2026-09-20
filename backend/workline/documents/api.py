"""FastAPI endpoints for the Document Intelligence Pipeline."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.workline.documents.models import DocumentRecord, SourceType
from backend.workline.documents.service import document_service

router = APIRouter(prefix="/api/documents", tags=["Document Intelligence"])


class IngestDocumentRequest(BaseModel):
    document_id: str
    project_id: str
    content: str
    filename: str
    source_type: SourceType = SourceType.DATASHEET
    team_id: str = "default_team"


@router.post("/ingest", response_model=DocumentRecord)
def ingest_document(req: IngestDocumentRequest) -> DocumentRecord:
    return document_service.ingest_document(
        document_id=req.document_id,
        project_id=req.project_id,
        content=req.content,
        filename=req.filename,
        source_type=req.source_type,
        team_id=req.team_id,
    )


@router.get("", response_model=List[DocumentRecord])
def list_documents(project_id: Optional[str] = None) -> List[DocumentRecord]:
    return document_service.list_documents(project_id)


@router.get("/datasheets")
def get_datasheets_endpoint(project_id: str) -> List[Dict[str, Any]]:
    """
    Get all linked manufacturer datasheets for a project from the Document Knowledge Base.
    """
    from backend.workline.documents.nexar_bridge import nexar_knowledge_bridge
    return nexar_knowledge_bridge.get_project_datasheets(project_id)


@router.get("/{document_id}", response_model=DocumentRecord)
def get_document(document_id: str) -> DocumentRecord:
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/entities")
def get_document_entities(document_id: str) -> List[Dict[str, Any]]:
    entities = document_service.get_entities(document_id)
    return [e.model_dump() for e in entities]


@router.get("/{document_id}/structure")
def get_document_structure(document_id: str) -> Dict[str, Any]:
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": doc.document_id,
        "title": doc.title,
        "sections": [s.model_dump() for s in doc.sections],
        "metadata": doc.metadata,
    }


@router.post("/{document_id}/reindex", response_model=DocumentRecord)
def reindex_document(document_id: str) -> DocumentRecord:
    try:
        return document_service.reindex_document(document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{document_id}")
def delete_document(document_id: str) -> Dict[str, Any]:
    success = document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "DELETED", "document_id": document_id}


# ============================================================================
# OCTOPART / NEXAR MCP KNOWLEDGE BASE INTEGRATION ENDPOINTS
# ============================================================================

class NexarSearchRequest(BaseModel):
    query: str
    limit: int = 10
    project_id: Optional[str] = None


class SaveToKnowledgePayload(BaseModel):
    project_id: str
    component_data: Dict[str, Any]
    team_id: str = "default_team"


class AddToBomPayload(BaseModel):
    project_id: str
    component_data: Dict[str, Any]
    quantity: int = 1
    reference_designator: Optional[str] = None


@router.post("/nexar/search")
async def search_nexar_mcp(req: NexarSearchRequest) -> Dict[str, Any]:
    """
    Search electronic components in Octopart / Nexar catalog through MCP.
    """
    from backend.workline.documents.nexar_bridge import nexar_knowledge_bridge
    try:
        candidates = await nexar_knowledge_bridge.search_nexar_components(req.query, limit=req.limit)
        return {
            "query": req.query,
            "source": "Octopart / Nexar MCP",
            "count": len(candidates),
            "results": candidates,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Nexar MCP query failed: {str(exc)}")


@router.post("/nexar/save-to-knowledge")
async def save_nexar_to_knowledge_base(payload: SaveToKnowledgePayload) -> Dict[str, Any]:
    """
    Normalize Nexar component data, store in SurrealDB knowledge graph,
    prevent duplicates, and index into the Documents Library.
    """
    from backend.workline.documents.nexar_bridge import nexar_knowledge_bridge
    try:
        res = await nexar_knowledge_bridge.save_to_knowledge_base(
            project_id=payload.project_id,
            comp_dict=payload.component_data,
            team_id=payload.team_id,
        )
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save component to knowledge base: {str(exc)}")


@router.post("/nexar/add-to-bom")
async def add_nexar_to_bom(payload: AddToBomPayload) -> Dict[str, Any]:
    """
    Directly add the selected Nexar component to the active project BOM.
    """
    from backend.workline.documents.nexar_bridge import nexar_knowledge_bridge
    try:
        res = await nexar_knowledge_bridge.add_to_bom(
            project_id=payload.project_id,
            comp_dict=payload.component_data,
            quantity=payload.quantity,
            reference_designator=payload.reference_designator,
        )
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to add component to BOM: {str(exc)}")


class GenerateKnowledgeBasePayload(BaseModel):
    project_id: str
    idea: Optional[str] = None
    components: Optional[List[Dict[str, Any]]] = None
    team_id: str = "default_team"


@router.post("/nexar/generate-knowledge-base")
async def generate_knowledge_base_endpoint(payload: GenerateKnowledgeBasePayload) -> Dict[str, Any]:
    """
    Generate complete Engineering Knowledge Base by accessing manufacturer component datasheets
    via the Octopart / Nexar API.
    """
    from backend.workline.documents.nexar_bridge import nexar_knowledge_bridge
    try:
        res = await nexar_knowledge_bridge.generate_knowledge_base_from_components(
            project_id=payload.project_id,
            idea=payload.idea,
            components=payload.components,
            team_id=payload.team_id,
        )
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Knowledge Base generation failed: {str(exc)}")

