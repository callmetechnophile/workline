"""Gamma API client and presentation renderer."""

import asyncio
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.workline.generation.models import (
    GeneratedPresentationArtifact,
    PresentationGenerationRequest,
    PresentationOutline,
)
from backend.workline.generation.presentation.prompts import PresentationContextBuilder


class GammaClient:
    """Client for generating structured technical presentation decks via Gamma."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._jobs: Dict[str, Dict[str, Any]] = {}

    async def render_presentation(self, request: PresentationGenerationRequest) -> GeneratedPresentationArtifact:
        """Render a structured presentation artifact from project context."""
        self._jobs[request.request_id] = {"status": "PROCESSING"}
        await asyncio.sleep(0.05)  # Simulate network / engine latency

        # Build grounded outline
        outline = PresentationContextBuilder.build_outline(
            project_id=request.project_id,
            title=request.title,
            audience=request.audience,
            purpose=request.purpose,
            slide_count=request.slide_count,
            custom_sections=request.source_sections,
        )

        artifact_id = f"art_pres_{uuid.uuid4().hex[:8]}"
        deck_content = self._render_markdown_deck(outline)
        output_hash = hashlib.sha256(deck_content.encode("utf-8")).hexdigest()

        artifact = GeneratedPresentationArtifact(
            artifact_id=artifact_id,
            project_id=request.project_id,
            request_id=request.request_id,
            title=request.title,
            filename=f"{request.project_id}_presentation_{artifact_id}.md",
            format="markdown",
            slide_count=len(outline.slides),
            size=len(deck_content.encode("utf-8")),
            sha256=output_hash,
            provider="Gamma",
            model="gamma-v2",
            outline=outline,
            content=deck_content,
        )

        self._jobs[request.request_id] = {"status": "COMPLETED", "artifact": artifact}
        return artifact

    def get_job_status(self, request_id: str) -> str:
        """Query job status."""
        return self._jobs.get(request_id, {}).get("status", "UNKNOWN")

    def cancel_job(self, request_id: str) -> bool:
        """Cancel in-flight job."""
        if request_id in self._jobs:
            self._jobs[request_id]["status"] = "CANCELLED"
            return True
        return False

    def get_job_artifact(self, request_id: str) -> Optional[GeneratedPresentationArtifact]:
        """Fetch completed artifact."""
        return self._jobs.get(request_id, {}).get("artifact")

    def _render_markdown_deck(self, outline: PresentationOutline) -> str:
        """Render outline into Marp/Gamma compatible Markdown presentation deck."""
        lines = [
            "---",
            "marp: true",
            "theme: gaia",
            f"title: {outline.title}",
            "paginate: true",
            "backgroundColor: #09090b",
            "color: #f4f4f5",
            "---",
            "",
            f"# {outline.title}",
            f"### {outline.subtitle or ''}",
            f"**Audience**: {outline.audience} | **Purpose**: {outline.purpose.value}",
            "",
        ]

        for idx, slide in enumerate(outline.slides, start=1):
            lines.append("---")
            lines.append("")
            lines.append(f"## Slide {idx}: {slide.title}")
            lines.append(f"*{slide.objective}*")
            lines.append("")
            for pt in slide.key_points:
                lines.append(f"- {pt}")
            lines.append("")
            if slide.visual_requirements:
                lines.append(f"> **Visual**: {slide.visual_requirements}")
                lines.append("")
            if slide.source_objects:
                lines.append(f"*Sources*: `{', '.join(slide.source_objects)}`")
                lines.append("")
            if slide.speaker_notes:
                lines.append(f"<!-- Speaker Notes: {slide.speaker_notes} -->")
                lines.append("")

        return "\n".join(lines)
