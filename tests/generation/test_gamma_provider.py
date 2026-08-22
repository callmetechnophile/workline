"""Tests for Gamma presentation generation provider, outline builder, and factuality."""

import pytest
from backend.workline.generation.models import PresentationGenerationRequest, PresentationPurpose, SlideType
from backend.workline.generation.presentation.prompts import PresentationContextBuilder
from backend.workline.generation.presentation.provider import GammaProvider
from backend.workline.generation.presentation.validation import PresentationValidator


@pytest.mark.asyncio
async def test_gamma_provider_generation():
    provider = GammaProvider()
    assert provider.provider_name == "Gamma"

    req = PresentationGenerationRequest(
        project_id="rover_v2",
        team_id="alpha",
        title="Autonomous Rover Engineering Review",
        audience="Hardware Leads",
        purpose=PresentationPurpose.TECHNICAL_DEEP_DIVE,
        slide_count=7,
    )

    assert provider.validate_request(req) is True

    artifact = await provider.generate(req)
    assert artifact.project_id == "rover_v2"
    assert artifact.provider == "Gamma"
    assert artifact.format == "markdown"
    assert artifact.slide_count == 7
    assert artifact.content is not None
    assert "marp: true" in artifact.content
    assert "Slide 1:" in artifact.content


def test_presentation_context_builder_factuality():
    outline = PresentationContextBuilder.build_outline(
        project_id="satellite_system",
        title="Satellite Systems Engineering",
        audience="Aerospace Engineers",
        purpose=PresentationPurpose.PROJECT_OVERVIEW,
        slide_count=6,
    )

    assert outline.title == "Satellite Systems Engineering"
    assert len(outline.slides) == 6

    # Verify that slides have verified source objects
    for slide in outline.slides:
        assert len(slide.source_objects) >= 1
        assert any("satellite_system" in s for s in slide.source_objects)

    # Verify factuality validation
    is_valid, warnings = PresentationValidator.validate_outline_factuality(outline, ["Google ADK", "SurrealDB"])
    assert is_valid is True
