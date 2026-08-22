"""Tests for Generation Security, Zero Credential Leakage, and Project Isolation."""

import pytest
from backend.workline.generation.models import ImagePurpose
from backend.workline.generation.service import GenerationService


@pytest.mark.asyncio
async def test_zero_credential_leakage_in_artifacts():
    service = GenerationService()

    img_art = await service.generate_image(
        project_id="secure_proj",
        purpose=ImagePurpose.ARCHITECTURE,
    )

    art_dict = img_art.model_dump()
    dumped_str = str(art_dict)

    # Verify no secret fields exist in artifact model
    assert "api_key" not in dumped_str
    assert "secret" not in dumped_str
    assert "private_key" not in dumped_str
    assert "token" not in dumped_str


@pytest.mark.asyncio
async def test_project_artifact_isolation():
    service = GenerationService()

    await service.generate_image(project_id="proj_A", purpose=ImagePurpose.ARCHITECTURE)
    await service.generate_image(project_id="proj_B", purpose=ImagePurpose.PCB)

    proj_a_arts = service.list_artifacts("proj_A")
    proj_b_arts = service.list_artifacts("proj_B")

    assert len(proj_a_arts) >= 1
    assert len(proj_b_arts) >= 1
    assert all(a.project_id == "proj_A" for a in proj_a_arts)
    assert all(a.project_id == "proj_B" for a in proj_b_arts)
