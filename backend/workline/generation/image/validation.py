"""Validation logic for image generation requests and outputs."""

from typing import List, Tuple
from backend.workline.generation.models import ImageGenerationRequest


class ImageRequestValidator:
    """Validates parameters and size limits for image generation."""

    @classmethod
    def validate(cls, request: ImageGenerationRequest) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not request.project_id or not request.project_id.strip():
            errors.append("Missing required project_id")
        if not request.prompt or len(request.prompt.strip()) < 5:
            errors.append("Prompt must contain at least 5 characters")
        if request.aspect_ratio not in ("16:9", "4:3", "1:1", "9:16"):
            errors.append(f"Unsupported aspect ratio '{request.aspect_ratio}'")
        return (len(errors) == 0, errors)
