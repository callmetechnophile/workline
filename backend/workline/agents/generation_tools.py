"""Google ADK agent tools for Visual (Paper Banana) and Presentation (Gamma) generation."""

from typing import Any, Dict, Optional
from backend.workline.generation.models import ImagePurpose, PresentationPurpose
from backend.workline.generation.service import generation_service


async def generate_project_visual(
    project_id: str,
    purpose: str = "ARCHITECTURE",
    user_prompt: Optional[str] = None,
    aspect_ratio: str = "16:9",
    team_id: str = "default_team",
) -> Dict[str, Any]:
    """
    Google ADK tool: Generates a technical visualization via Paper Banana grounded in project architecture.
    """
    try:
        purpose_enum = ImagePurpose(purpose.upper())
    except ValueError:
        purpose_enum = ImagePurpose.ARCHITECTURE

    artifact = await generation_service.generate_image(
        project_id=project_id,
        purpose=purpose_enum,
        user_prompt=user_prompt,
        aspect_ratio=aspect_ratio,
        team_id=team_id,
    )

    return {
        "status": "COMPLETED",
        "artifact_id": artifact.artifact_id,
        "filename": artifact.filename,
        "format": artifact.format,
        "provider": artifact.provider,
        "sha256": artifact.sha256,
    }


async def generate_architecture_image(project_id: str, team_id: str = "default_team") -> Dict[str, Any]:
    """Google ADK tool: Synthesizes a system architecture diagram for the project."""
    return await generate_project_visual(
        project_id=project_id,
        purpose="ARCHITECTURE",
        team_id=team_id,
    )


async def generate_pcb_visual(project_id: str, team_id: str = "default_team") -> Dict[str, Any]:
    """Google ADK tool: Generates a PCB thermal layout and placement visualization."""
    return await generate_project_visual(
        project_id=project_id,
        purpose="PCB",
        team_id=team_id,
    )


async def generate_presentation(
    project_id: str,
    title: str,
    audience: str = "Technical Audience",
    purpose: str = "PROJECT_OVERVIEW",
    slide_count: int = 8,
    team_id: str = "default_team",
) -> Dict[str, Any]:
    """
    Google ADK tool: Generates a structured technical presentation deck via Gamma.
    """
    try:
        purpose_enum = PresentationPurpose(purpose.upper())
    except ValueError:
        purpose_enum = PresentationPurpose.PROJECT_OVERVIEW

    artifact = await generation_service.generate_presentation(
        project_id=project_id,
        title=title,
        audience=audience,
        purpose=purpose_enum,
        slide_count=slide_count,
        team_id=team_id,
    )

    return {
        "status": "COMPLETED",
        "artifact_id": artifact.artifact_id,
        "title": artifact.title,
        "slide_count": artifact.slide_count,
        "format": artifact.format,
        "provider": artifact.provider,
        "sha256": artifact.sha256,
    }


async def generate_hackathon_deck(project_id: str, title: str, team_id: str = "default_team") -> Dict[str, Any]:
    """Google ADK tool: Generates a high-impact hackathon presentation deck."""
    return await generate_presentation(
        project_id=project_id,
        title=title,
        audience="Hackathon Judges & Engineers",
        purpose="HACKATHON",
        slide_count=7,
        team_id=team_id,
    )
