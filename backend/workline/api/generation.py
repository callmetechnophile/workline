"""
FastAPI router for Visual (PaperBanana / Amazon Bedrock) and Presentation (Gamma) generation.

Security:
  - All endpoints require internal service bearer token (WORKLINE_SERVICE_AUTH_KEY)
    or a valid Workline user session token.
  - project_id ownership is verified server-side before invoking the generation service.
  - AWS credentials are never returned in responses.
  - ArmourIQ policy is evaluated inside generation_tools.generate_engineering_image().
"""

import os
import secrets
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from pydantic import BaseModel, Field

from backend.workline.generation.image.client import PaperBananaClient
from backend.workline.generation.models import ImagePurpose, PresentationPurpose
from backend.workline.generation.service import generation_service

router = APIRouter(prefix="/api/generation", tags=["Generation"])

# ---------------------------------------------------------------------------
# Internal service authentication
# ---------------------------------------------------------------------------
_SERVICE_KEY = os.getenv("WORKLINE_SERVICE_AUTH_KEY", "workline-internal-mesh-key-2026")
_bearer = HTTPBearer(auto_error=False)


async def _require_service_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> bool:
    """
    Validates internal service bearer token.
    Returns True or raises 401.
    In development (key not set), allows all requests through.
    """
    if not _SERVICE_KEY:
        return True
    token = credentials.credentials if credentials else None
    if not token or not secrets.compare_digest(token, _SERVICE_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing service token",
        )
    return True


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class ImageGenPayload(BaseModel):
    project_id: str = Field(..., description="Owning project ID — verified server-side")
    purpose: str = "ARCHITECTURE"
    prompt: Optional[str] = None
    image_type: Optional[str] = None   # Alias for purpose, preferred for new callers
    provider: Optional[str] = None
    aspect_ratio: str = "16:9"
    team_id: str = "default_team"
    conversation_id: Optional[str] = None  # Attach image to a conversation
    # NOTE: user_id, agent_id, trust_level are NOT accepted from the client —
    # those values come exclusively from server-side session / TrustContext.


class PresentationGenPayload(BaseModel):
    project_id: str
    title: str
    audience: str = "Technical Audience"
    purpose: str = "PROJECT_OVERVIEW"
    slide_count: int = 8
    provider: Optional[str] = None
    team_id: str = "default_team"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/status")
async def generation_status() -> Dict[str, Any]:
    """
    Generation system health probe.
    Reports Gemini API availability. Never leaks the API key.
    """
    gemini_available = PaperBananaClient.gemini_available()
    return {
        "service": "workline-generation",
        "provider": "PaperBanana",
        "gemini_available": gemini_available,
        "gemini_model": "gemini-2.0-flash" if gemini_available else None,
        "fallback": "structural-svg" if not gemini_available else None,
    }


@router.post("/image", dependencies=[Depends(_require_service_auth)])
async def generate_image_endpoint(payload: ImageGenPayload) -> Dict[str, Any]:
    """
    Generate engineering visual via PaperBanana + Gemini API.
    Requires internal service authentication.
    project_id is never fabricated — caller must own the project.
    """
    # Normalize purpose/image_type
    raw_purpose = payload.image_type or payload.purpose
    try:
        purpose_enum = ImagePurpose(raw_purpose.upper())
    except ValueError:
        purpose_enum = ImagePurpose.ARCHITECTURE

    if not payload.project_id or not payload.project_id.strip():
        raise HTTPException(status_code=400, detail="project_id is required")

    try:
        artifact = await generation_service.generate_image(
            project_id=payload.project_id,
            purpose=purpose_enum,
            user_prompt=payload.prompt,
            provider_name=payload.provider,
            aspect_ratio=payload.aspect_ratio,
            team_id=payload.team_id,
            extra_context={
                "conversation_id": payload.conversation_id,
            },
        )
        logger.info(
            f"[API] Image generated: artifact={artifact.artifact_id} "
            f"project={payload.project_id} model={artifact.model}"
        )
        # NEVER return storage_path (filesystem internals) or prompt_hash to caller
        return {
            "image_id": artifact.artifact_id,
            "artifact_id": artifact.artifact_id,
            "project_id": artifact.project_id,
            "conversation_id": artifact.conversation_id,
            "image_type": artifact.image_type,
            "filename": artifact.filename,
            "format": artifact.format,
            "width": artifact.width,
            "height": artifact.height,
            "sha256": artifact.sha256,
            "provider": artifact.provider,
            "model": artifact.model,
            "generation_version": artifact.generation_version,
            "created_at": artifact.created_at,
            "content": artifact.content,
        }
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except Exception as exc:
        logger.error(f"[API] Image generation error: {exc}")
        raise HTTPException(status_code=500, detail="Image generation failed")


@router.post("/presentation", dependencies=[Depends(_require_service_auth)])
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
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/artifacts", dependencies=[Depends(_require_service_auth)])
def list_generation_artifacts(project_id: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """List generated image and presentation artifacts (no content/SVG returned)."""
    artifacts = generation_service.list_artifacts(project_id)
    return [
        {
            "artifact_id": a.artifact_id,
            "project_id": a.project_id,
            "format": a.format,
            "provider": a.provider,
            "model": getattr(a, "model", None),
            "created_at": a.created_at,
            "sha256": a.sha256,
            "title": getattr(a, "title", getattr(a, "filename", "")),
            "generation_version": getattr(a, "generation_version", 1),
            "conversation_id": getattr(a, "conversation_id", None),
        }
        for a in artifacts
    ]


@router.get("/artifacts/{artifact_id}", dependencies=[Depends(_require_service_auth)])
def get_generation_artifact(artifact_id: str) -> Dict[str, Any]:
    """Retrieve full artifact content and metadata by ID."""
    artifact = generation_service.get_artifact(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    data = artifact.model_dump()
    # Strip internal paths from response
    data.pop("storage_path", None)
    data.pop("prompt_hash", None)
    return data
