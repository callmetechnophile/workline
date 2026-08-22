"""Tests for Paper Banana visual generation provider, prompts, and artifacts."""

import pytest
from backend.workline.generation.image.prompts import ImagePromptBuilder
from backend.workline.generation.image.provider import PaperBananaProvider
from backend.workline.generation.models import ImageGenerationRequest, ImagePurpose


@pytest.mark.asyncio
async def test_paperbanana_provider_generation():
    provider = PaperBananaProvider()
    assert provider.provider_name == "PaperBanana"

    req = ImageGenerationRequest(
        project_id="rover_vision",
        team_id="alpha",
        purpose=ImagePurpose.ARCHITECTURE,
        prompt="Workline multi-agent autonomous engineering architecture",
        aspect_ratio="16:9",
    )

    assert provider.validate_request(req) is True

    artifact = await provider.generate(req)
    assert artifact.project_id == "rover_vision"
    assert artifact.provider == "PaperBanana"
    assert artifact.format == "svg"
    assert artifact.sha256 != ""
    assert artifact.content is not None
    assert "<svg" in artifact.content
    assert "WORKLINE" in artifact.content


def test_image_prompt_builder_grounding():
    # Verify architecture prompt contains authentic project technologies
    arch_prompt = ImagePromptBuilder.build_prompt("satellite_v1", ImagePurpose.ARCHITECTURE)
    assert "Google ADK" in arch_prompt
    assert "SurrealDB" in arch_prompt
    assert "Qdrant" in arch_prompt
    assert "Bindu A2A" in arch_prompt
    assert "Corsair" in arch_prompt
    assert "TypeScript 7" in arch_prompt

    # Verify PCB prompt contains board specifications
    pcb_prompt = ImagePromptBuilder.build_prompt("sensor_hub", ImagePurpose.PCB, extra_context={"board_width": 120.0})
    assert "120.0mm" in pcb_prompt
    assert "PINN" in pcb_prompt
    assert "MCU" in pcb_prompt
