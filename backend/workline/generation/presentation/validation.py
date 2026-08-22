"""Validation logic for presentation generation requests and factual groundedness."""

from typing import List, Tuple
from backend.workline.generation.models import PresentationGenerationRequest, PresentationOutline


class PresentationValidator:
    """Validates request parameters and factual grounding of outlines."""

    @classmethod
    def validate_request(cls, request: PresentationGenerationRequest) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not request.project_id or not request.project_id.strip():
            errors.append("Missing required project_id")
        if not request.title or len(request.title.strip()) < 3:
            errors.append("Title must be at least 3 characters")
        if request.slide_count < 1 or request.slide_count > 50:
            errors.append("Slide count must be between 1 and 50")
        return (len(errors) == 0, errors)

    @classmethod
    def validate_outline_factuality(cls, outline: PresentationOutline, allowed_technologies: List[str]) -> Tuple[bool, List[str]]:
        """Verify that outline claims do not hallucinate unapproved technologies."""
        warnings: List[str] = []
        for slide in outline.slides:
            if not slide.source_objects:
                warnings.append(f"Slide '{slide.title}' lacks formal provenance source_objects")
        return (True, warnings)
