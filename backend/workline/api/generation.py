"""FastAPI router for Visual (Paper Banana) and Presentation (Gamma) generation."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from backend.workline.generation.models import ImagePurpose, PresentationPurpose
from backend.workline.generation.service import generation_service

router = APIRouter(prefix="/api/generation", tags=["Generation"])


class ImageGenPayload(BaseModel):
    project_id: str
    purpose: str = "ARCHITECTURE"
    prompt: Optional[str] = None
    provider: Optional[str] = None
    aspect_ratio: str = "16:9"
    team_id: str = "default_team"


class PresentationGenPayload(BaseModel):
    project_id: str
    title: str
    audience: str = "Technical Audience"
    purpose: str = "PROJECT_OVERVIEW"
    slide_count: int = 8
    provider: Optional[str] = None
    team_id: str = "default_team"


@router.post("/image")
async def generate_image_endpoint(payload: ImageGenPayload) -> Dict[str, Any]:
    """Generate technical visualization diagram via Paper Banana."""
    try:
        purpose_enum = ImagePurpose(payload.purpose.upper())
    except ValueError:
        purpose_enum = ImagePurpose.ARCHITECTURE

    try:
        artifact = await generation_service.generate_image(
            project_id=payload.project_id,
            purpose=purpose_enum,
            user_prompt=payload.prompt,
            provider_name=payload.provider,
            aspect_ratio=payload.aspect_ratio,
            team_id=payload.team_id,
        )
        return {
            "artifact_id": artifact.artifact_id,
            "filename": artifact.filename,
            "format": artifact.format,
            "width": artifact.width,
            "height": artifact.height,
            "sha256": artifact.sha256,
            "provider": artifact.provider,
            "content": artifact.content,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/presentation")
async def generate_presentation_endpoint(payload: PresentationGenPayload) -> Dict[str, Any]:
    """Generate technical presentation deck via Gamma."""
    try:
        purpose_enum = PresentationPurpose(payload.purpose.upper())
    except ValueError:
        purpose_enum = PresentationPurpose.PROJECT_OVERVIEW

    try:
        artifact = await generation_service.generate_presentation(
            project_id=payload.project_id,
            title=payload.title,
            audience=payload.audience,
            purpose=purpose_enum,
            slide_count=payload.slide_count,
            provider_name=payload.provider,
            team_id=payload.team_id,
        )
        return {
            "artifact_id": artifact.artifact_id,
            "title": artifact.title,
            "slide_count": artifact.slide_count,
            "format": artifact.format,
            "sha256": artifact.sha256,
            "provider": artifact.provider,
            "content": artifact.content,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/artifacts")
def list_generation_artifacts(project_id: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """List generated image and presentation artifacts."""
    artifacts = generation_service.list_artifacts(project_id)
    return [
        {
            "artifact_id": a.artifact_id,
            "project_id": a.project_id,
            "format": a.format,
            "provider": a.provider,
            "created_at": a.created_at,
            "sha256": a.sha256,
            "title": getattr(a, "title", getattr(a, "filename", "")),
        }
        for a in artifacts
    ]


@router.get("/artifacts/{artifact_id}")
def get_generation_artifact(artifact_id: str) -> Dict[str, Any]:
    """Retrieve full artifact content and metadata."""
    artifact = generation_service.get_artifact(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact.model_dump()
