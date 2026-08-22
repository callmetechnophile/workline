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
