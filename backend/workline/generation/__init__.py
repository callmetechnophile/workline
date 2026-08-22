"""Workline Visual (Paper Banana) and Presentation (Gamma) generation package."""

from backend.workline.generation.models import (
    GeneratedImageArtifact,
    GeneratedPresentationArtifact,
    GenerationStatus,
    ImageGenerationRequest,
    ImagePurpose,
    PresentationGenerationRequest,
    PresentationOutline,
    PresentationPurpose,
    SlideContent,
    SlideType,
)
from backend.workline.generation.registry import (
    GenerationRegistry,
    ImageGenerationProvider,
    PresentationGenerationProvider,
    generation_registry,
)
from backend.workline.generation.service import GenerationService, generation_service

__all__ = [
    "GenerationService",
    "generation_service",
    "GenerationRegistry",
    "generation_registry",
    "ImageGenerationProvider",
    "PresentationGenerationProvider",
    "ImageGenerationRequest",
    "PresentationGenerationRequest",
    "GeneratedImageArtifact",
    "GeneratedPresentationArtifact",
    "ImagePurpose",
    "PresentationPurpose",
    "PresentationOutline",
    "SlideContent",
    "SlideType",
    "GenerationStatus",
]
