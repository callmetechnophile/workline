"""Tests for GenerationService, rate limits, cost limits, and artifact retrieval."""

import pytest
from backend.workline.generation.models import ImagePurpose, PresentationPurpose
from backend.workline.generation.service import GenerationService


@pytest.mark.asyncio
async def test_generation_service_image_and_presentation():
    service = GenerationService(rate_limit_window_seconds=60.0, max_requests_per_window=10)

    # 1. Generate Image
    img_art = await service.generate_image(
        project_id="test_proj_1",
        purpose=ImagePurpose.ARCHITECTURE,
        user_prompt="Focus on multi-agent planner",
    )
    assert img_art.project_id == "test_proj_1"
    assert img_art.provider == "PaperBanana"

    # 2. Generate Presentation
    pres_art = await service.generate_presentation(
        project_id="test_proj_1",
        title="Project Review Deck",
        slide_count=5,
    )
    assert pres_art.project_id == "test_proj_1"
    assert pres_art.provider == "Gamma"
    assert pres_art.slide_count == 5

    # 3. List and get artifacts
    artifacts = service.list_artifacts("test_proj_1")
    assert len(artifacts) == 2
    assert service.get_artifact(img_art.artifact_id) is not None
    assert service.get_artifact(pres_art.artifact_id) is not None


@pytest.mark.asyncio
async def test_rate_limiting_enforcement():
    # Set tight rate limit: max 2 requests per window
    service = GenerationService(rate_limit_window_seconds=10.0, max_requests_per_window=2)

    await service.generate_image(project_id="p_limit", purpose=ImagePurpose.ARCHITECTURE)
    await service.generate_image(project_id="p_limit", purpose=ImagePurpose.PCB)

    # Third request must raise RuntimeError
    with pytest.raises(RuntimeError, match="rate limit exceeded"):
        await service.generate_image(project_id="p_limit", purpose=ImagePurpose.WORKFLOW)


@pytest.mark.asyncio
async def test_cost_limit_enforcement():
    # Set tight cost limit: $0.10
    service = GenerationService(max_cost_limit=0.10)

    # 1 image = $0.05
    await service.generate_image(project_id="p_cost", purpose=ImagePurpose.ARCHITECTURE)
    # 2nd image = $0.05 (total = $0.10)
    await service.generate_image(project_id="p_cost", purpose=ImagePurpose.PCB)

    # 3rd image would exceed $0.10
    with pytest.raises(RuntimeError, match="cost limit exceeded"):
        await service.generate_image(project_id="p_cost", purpose=ImagePurpose.WORKFLOW)
