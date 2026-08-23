"""
Google ADK agent tools for Visual (PaperBanana / Amazon Bedrock) and Presentation (Gamma) generation.

Architecture:
  ADK Agent calls generate_engineering_image(...)
        ↓
  ArmourIQ: capability=IMAGE_GENERATION, risk=MEDIUM
        ↓
  ALLOW
        ↓
  PaperBananaClient → BedrockImageEngine → Amazon Bedrock
        ↓
  GeneratedImageArtifact (stored R2 + metadata R3)

Security posture:
  - project_id, agent_id, trust context come from server-side execution context
  - The ADK tool schema does NOT accept user_id/trust_level/agent_id from the browser
  - ArmourIQ policy is evaluated before generation service is called
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from backend.workline.armouriq.capabilities import AgentCapability, PolicyDecision, RiskTier
from backend.workline.armouriq.policy import ArmourIQPolicyEngine
from backend.workline.armouriq.trust_context import TrustContext
from backend.workline.generation.models import ImagePurpose, PresentationPurpose
from backend.workline.generation.service import generation_service


# ---------------------------------------------------------------------------
# ArmourIQ Policy Engine (singleton)
# ---------------------------------------------------------------------------
_policy = ArmourIQPolicyEngine()


def _check_image_authorization(
    context: TrustContext,
    tool_name: str = "generate_engineering_image",
) -> None:
    """
    Evaluate ArmourIQ policy before invoking any image generation tool.
    Raises PermissionError on DENY.
    """
    decision, reason = _policy.evaluate_tool_execution(
        tool_name=tool_name,
        parameters={"image_type": "ARCHITECTURE"},
        context=context,
    )
    if decision != PolicyDecision.ALLOW:
        raise PermissionError(
            f"ArmourIQ DENIED image generation: agent='{context.agent_id}' "
            f"project='{context.project_id}' decision={decision.value} reason={reason}"
        )


# ---------------------------------------------------------------------------
# Canonical ADK Tool: generate_engineering_image
# ---------------------------------------------------------------------------

async def generate_engineering_image(
    project_id: str,
    prompt: str,
    image_type: str = "ARCHITECTURE",
    style: str = "engineering",
    references: Optional[List[str]] = None,
    aspect_ratio: str = "16:9",
    conversation_id: Optional[str] = None,
    context: Optional[TrustContext] = None,
) -> Dict[str, Any]:
    """
    Google ADK tool: Generate an engineering visual via PaperBanana + Gemini API.

    Parameters are engineering-domain structured (image_type, style, references).
    project_id is validated server-side — never trusted from a raw browser request.
    agent_id, user_id, and trust_level come exclusively from the TrustContext.

    Returns: image_id, project_id, format, sha256, content (SVG), model, created_at.
    Never returns the GEMINI_API_KEY or any internal credentials.
    """
    # Build a minimal trust context if none provided (unit-test / CLI path)
    if context is None:
        context = TrustContext(
            session_id=f"adk_tool_{project_id}",
            project_id=project_id,
            agent_id="workline.generation_agent",
            capabilities=[AgentCapability.IMAGE_GENERATION],
        )

    # ArmourIQ policy evaluation — fail-closed
    _check_image_authorization(context, "generate_engineering_image")

    try:
        purpose_enum = ImagePurpose(image_type.upper())
    except ValueError:
        purpose_enum = ImagePurpose.ARCHITECTURE

    artifact = await generation_service.generate_image(
        project_id=project_id,
        purpose=purpose_enum,
        user_prompt=prompt,
        aspect_ratio=aspect_ratio,
        team_id=getattr(context, "user_id", "adk"),
        extra_context={
            "style": style,
            "references": references or [],
            "conversation_id": conversation_id,
        },
    )

    logger.info(
        f"[PaperBanana] Image generated: artifact_id={artifact.artifact_id} "
        f"project={project_id} model={artifact.model} conversation={conversation_id}"
    )

    return {
        "status": "COMPLETED",
        "image_id": artifact.artifact_id,
        "project_id": artifact.project_id,
        "conversation_id": conversation_id,
        "image_type": image_type,
        "format": artifact.format,
        "model": artifact.model,
        "provider": artifact.provider,
        "sha256": artifact.sha256,
        "generation_version": artifact.generation_version,
        "created_at": artifact.created_at,
        "content": artifact.content,
    }


# ---------------------------------------------------------------------------
# Convenience wrappers (backward-compatible with existing ADK agent calls)
# ---------------------------------------------------------------------------

async def generate_project_visual(
    project_id: str,
    purpose: str = "ARCHITECTURE",
    user_prompt: Optional[str] = None,
    aspect_ratio: str = "16:9",
    team_id: str = "default_team",
    context: Optional[TrustContext] = None,
) -> Dict[str, Any]:
    """Google ADK tool: Generates a technical visualization via Paper Banana + Gemini."""
    return await generate_engineering_image(
        project_id=project_id,
        prompt=user_prompt or f"Technical {purpose.lower()} diagram for project {project_id}",
        image_type=purpose,
        context=context,
    )


async def generate_architecture_image(
    project_id: str,
    team_id: str = "default_team",
    context: Optional[TrustContext] = None,
) -> Dict[str, Any]:
    """Google ADK tool: Synthesizes a system architecture diagram for the project."""
    return await generate_engineering_image(
        project_id=project_id,
        prompt=f"System architecture diagram for project {project_id}",
        image_type="ARCHITECTURE",
        context=context,
    )


async def generate_pcb_visual(
    project_id: str,
    team_id: str = "default_team",
    context: Optional[TrustContext] = None,
) -> Dict[str, Any]:
    """Google ADK tool: Generates a PCB thermal layout and placement visualization."""
    return await generate_engineering_image(
        project_id=project_id,
        prompt=f"PCB layout and thermal distribution diagram for project {project_id}",
        image_type="PCB",
        context=context,
    )


async def generate_presentation(
    project_id: str,
    title: str,
    audience: str = "Technical Audience",
    purpose: str = "PROJECT_OVERVIEW",
    slide_count: int = 8,
    team_id: str = "default_team",
    context: Optional[TrustContext] = None,
) -> Dict[str, Any]:
    """Google ADK tool: Generates a structured technical presentation deck via Gamma."""
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


async def generate_hackathon_deck(
    project_id: str,
    title: str,
    team_id: str = "default_team",
) -> Dict[str, Any]:
    """Google ADK tool: Generates a high-impact hackathon presentation deck."""
    return await generate_presentation(
        project_id=project_id,
        title=title,
        audience="Hackathon Judges & Engineers",
        purpose="HACKATHON",
        slide_count=7,
        team_id=team_id,
    )
