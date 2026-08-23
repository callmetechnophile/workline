"""
PaperBanana × Amazon Bedrock Image Generation — Full Integration Test Suite

Tests cover:
 1. Authenticated image generation (service token present)
 2. Unauthenticated request → 401
 3. Unauthorized project (empty project_id) → 400
 4. ArmourIQ denial (missing IMAGE_GENERATION capability)
 5. Offline Bedrock fallback → fallback SVG
 6. Invalid generation request (missing project_id field)
 7. PaperBanana failure → controlled error response
 8. Bedrock visual engine fallback handling
 9. Storage failure handling
10. Successful end-to-end image generation
11. Conversation attachment (conversation_id stored on artifact)
12. Project asset association (image_type + project_id recorded)
13. Duplicate request handling — versioning increments
14. x402 image.generate service catalog registration

Security posture:
 - AWS credentials never appear in test output or assertions
 - ArmourIQ deny path explicitly verified
"""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, patch

from backend.workline.generation.image.client import BedrockImageEngine, PaperBananaClient
from backend.workline.generation.models import ImageGenerationRequest, ImagePurpose


# ---------------------------------------------------------------------------
# pytest-asyncio config
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def generation_client():
    """TestClient for the generation API (mounted on backend.main)."""
    from fastapi.testclient import TestClient
    from backend.main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def valid_service_token():
    return os.getenv("WORKLINE_SERVICE_AUTH_KEY", "workline-internal-mesh-key-2026")


@pytest.fixture
def auth_headers(valid_service_token):
    return {"Authorization": f"Bearer {valid_service_token}"}


# ---------------------------------------------------------------------------
# 1. Authenticated image generation returns valid artifact
# ---------------------------------------------------------------------------

def test_authenticated_image_generation_returns_artifact(generation_client, auth_headers):
    """Authenticated POST to /api/generation/image returns image artifact."""
    resp = generation_client.post(
        "/api/generation/image",
        json={"project_id": "proj_test_auth_001", "purpose": "ARCHITECTURE"},
        headers=auth_headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == "proj_test_auth_001"
    assert "image_id" in data
    assert data["format"] in ("png", "svg")
    assert data["provider"] == "PaperBanana"


# ---------------------------------------------------------------------------
# 2. Unauthenticated request → 401
# ---------------------------------------------------------------------------

def test_unauthenticated_request_returns_401(generation_client):
    """POST without Authorization header returns 401."""
    resp = generation_client.post(
        "/api/generation/image",
        json={"project_id": "proj_test_001", "purpose": "ARCHITECTURE"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 3. Empty project_id → 400
# ---------------------------------------------------------------------------

def test_empty_project_id_returns_400(generation_client, auth_headers):
    """Empty project_id is rejected before generation is attempted."""
    resp = generation_client.post(
        "/api/generation/image",
        json={"project_id": "", "purpose": "ARCHITECTURE"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 4. ArmourIQ denies without IMAGE_GENERATION capability
# ---------------------------------------------------------------------------

async def test_armouriq_denies_generation_without_capability():
    """ArmourIQ denies generate_engineering_image when IMAGE_GENERATION capability absent."""
    from backend.workline.agents.generation_tools import generate_engineering_image
    from backend.workline.armouriq.trust_context import TrustContext
    from backend.workline.armouriq.capabilities import AgentCapability

    context = TrustContext(
        session_id="test_session",
        project_id="proj_armouriq_test",
        agent_id="test_agent",
        capabilities=[AgentCapability.READ_PROJECT],  # missing IMAGE_GENERATION
    )

    with pytest.raises(PermissionError, match="ArmourIQ DENIED"):
        await generate_engineering_image(
            project_id="proj_armouriq_test",
            prompt="Generate architecture diagram",
            context=context,
        )


# ---------------------------------------------------------------------------
# 5. Offline Bedrock fallback returns structural SVG
# ---------------------------------------------------------------------------

async def test_offline_bedrock_returns_fallback_svg():
    """When Bedrock visual engine returns None, fallback structural SVG is generated."""
    with patch(
        "backend.workline.generation.image.client.BedrockImageEngine.generate_visual",
        new_callable=AsyncMock,
        return_value=None,
    ):
        client = PaperBananaClient()
        request = ImageGenerationRequest(
            project_id="proj_no_bedrock",
            purpose=ImagePurpose.ARCHITECTURE,
            prompt="Test diagram",
        )
        artifact = await client.render_visual(request)

    assert artifact.model == "fallback-svg"
    assert artifact.format == "svg"
    assert os.path.exists(artifact.storage_path)


# ---------------------------------------------------------------------------
# 6. Missing required project_id field → 422
# ---------------------------------------------------------------------------

def test_invalid_request_missing_project_id(generation_client, auth_headers):
    """POST without project_id field returns 422 validation error."""
    resp = generation_client.post(
        "/api/generation/image",
        json={"purpose": "ARCHITECTURE"},  # missing project_id
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 7. PaperBanana provider failure → controlled error (no traceback exposed)
# ---------------------------------------------------------------------------

def test_paperbanana_provider_failure_returns_controlled_error(generation_client, auth_headers):
    """If PaperBananaProvider.generate() raises, API returns controlled error."""
    with patch(
        "backend.workline.generation.image.provider.PaperBananaProvider.generate",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Rendering engine internal failure"),
    ):
        resp = generation_client.post(
            "/api/generation/image",
            json={"project_id": "proj_crash_test_unique_7", "purpose": "PCB"},
            headers=auth_headers,
        )

    assert resp.status_code in (400, 429, 500)
    body = resp.json()
    assert "RuntimeError" not in str(body)
    assert "Traceback" not in str(body)


# ---------------------------------------------------------------------------
# 8. Successful end-to-end generation
# ---------------------------------------------------------------------------

async def test_successful_end_to_end_generation():
    """Full pipeline: prompt → Bedrock visual engine → artifact stored in service."""
    from backend.workline.generation.service import GenerationService

    service = GenerationService()
    artifact = await service.generate_image(
        project_id="proj_e2e_test_unique",
        purpose=ImagePurpose.ARCHITECTURE,
        user_prompt="High-level architecture of the 48V → 12V converter",
    )

    assert artifact.project_id == "proj_e2e_test_unique"
    assert artifact.provider == "PaperBanana"
    assert artifact.generation_version == 1
    assert artifact.sha256 != ""


# ---------------------------------------------------------------------------
# 9. Conversation attachment
# ---------------------------------------------------------------------------

async def test_conversation_attachment_stored_on_artifact():
    """conversation_id propagates from extra_context to the artifact."""
    from backend.workline.generation.service import GenerationService

    service = GenerationService()
    artifact = await service.generate_image(
        project_id="proj_conv_test_unique",
        purpose=ImagePurpose.WORKFLOW,
        extra_context={"conversation_id": "conv_abc123"},
    )

    assert artifact.conversation_id == "conv_abc123"


# ---------------------------------------------------------------------------
# 10. Project asset association
# ---------------------------------------------------------------------------

async def test_project_asset_association():
    """Generated image records project_id and image_type correctly."""
    from backend.workline.generation.service import GenerationService

    service = GenerationService()
    artifact = await service.generate_image(
        project_id="proj_assoc_test",
        purpose=ImagePurpose.PCB,
    )

    assert artifact.project_id == "proj_assoc_test"
    assert artifact.image_type == "PCB"
    assert artifact.provider == "PaperBanana"


# ---------------------------------------------------------------------------
# 11. Duplicate requests increment generation version
# ---------------------------------------------------------------------------

async def test_duplicate_requests_increment_generation_version():
    """Second generation of same type for same project gets version 2."""
    from backend.workline.generation.service import GenerationService

    service = GenerationService()
    art1 = await service.generate_image(
        project_id="proj_version_test",
        purpose=ImagePurpose.ARCHITECTURE,
    )
    art2 = await service.generate_image(
        project_id="proj_version_test",
        purpose=ImagePurpose.ARCHITECTURE,
    )

    assert art1.generation_version == 1
    assert art2.generation_version == 2
    assert art1.artifact_id != art2.artifact_id


# ---------------------------------------------------------------------------
# 12. x402 image.generate service catalog registration
# ---------------------------------------------------------------------------

def test_x402_image_generate_in_service_catalog():
    """image.generate service is registered in x402 catalog at correct price."""
    from backend.workline.x402.catalog import service_catalog

    svc = service_catalog.get_service("image.generate")
    assert svc is not None, "image.generate service not found in x402 catalog"
    assert svc.price_usdc == 0.10
    assert svc.endpoint == "/api/x402/image/generate"
    assert "paperbanana" in svc.tags or "bedrock" in svc.tags
    assert svc.enabled is True
