"""Provider interfaces and generation registry for Visual and Presentation generation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from backend.workline.generation.models import (
    GeneratedImageArtifact,
    GeneratedPresentationArtifact,
    ImageGenerationRequest,
    PresentationGenerationRequest,
)


class ImageGenerationProvider(ABC):
    """Abstract interface for image/technical visual generation providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'PaperBanana')."""
        pass

    @abstractmethod
    async def generate(self, request: ImageGenerationRequest) -> GeneratedImageArtifact:
        """Generate a technical visual artifact."""
        pass

    @abstractmethod
    def validate_request(self, request: ImageGenerationRequest) -> bool:
        """Validate request payload and parameters."""
        pass

    @abstractmethod
    async def get_status(self, request_id: str) -> str:
        """Query status of a generation job."""
        pass

    @abstractmethod
    async def cancel(self, request_id: str) -> bool:
        """Cancel an in-flight generation job."""
        pass

    @abstractmethod
    async def get_result(self, request_id: str) -> Optional[GeneratedImageArtifact]:
        """Fetch completed visual artifact."""
        pass


class PresentationGenerationProvider(ABC):
    """Abstract interface for presentation generation providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'Gamma')."""
        pass

    @abstractmethod
    async def generate(self, request: PresentationGenerationRequest) -> GeneratedPresentationArtifact:
        """Generate a structured presentation artifact."""
        pass

    @abstractmethod
    def validate_request(self, request: PresentationGenerationRequest) -> bool:
        """Validate request payload and outline parameters."""
        pass

    @abstractmethod
    async def get_status(self, request_id: str) -> str:
        """Query status of a presentation generation job."""
        pass

    @abstractmethod
    async def cancel(self, request_id: str) -> bool:
        """Cancel an in-flight presentation generation job."""
        pass

    @abstractmethod
    async def get_result(self, request_id: str) -> Optional[GeneratedPresentationArtifact]:
        """Fetch completed presentation artifact."""
        pass


class GenerationRegistry:
    """Registry coordinating available image and presentation generation providers."""

    def __init__(self):
        self._image_providers: Dict[str, ImageGenerationProvider] = {}
        self._presentation_providers: Dict[str, PresentationGenerationProvider] = {}

    def register_image_provider(self, provider: ImageGenerationProvider) -> None:
        """Register an image generation provider."""
        self._image_providers[provider.provider_name.lower()] = provider

    def register_presentation_provider(self, provider: PresentationGenerationProvider) -> None:
        """Register a presentation generation provider."""
        self._presentation_providers[provider.provider_name.lower()] = provider

    def get_image_provider(self, name: Optional[str] = None) -> Optional[ImageGenerationProvider]:
        """Get image provider by name or return the default."""
        if not self._image_providers:
            return None
        if name:
            return self._image_providers.get(name.lower())
        # Default to Paper Banana or first available
        return self._image_providers.get("paperbanana", next(iter(self._image_providers.values())))

    def get_presentation_provider(self, name: Optional[str] = None) -> Optional[PresentationGenerationProvider]:
        """Get presentation provider by name or return the default."""
        if not self._presentation_providers:
            return None
        if name:
            return self._presentation_providers.get(name.lower())
        # Default to Gamma or first available
        return self._presentation_providers.get("gamma", next(iter(self._presentation_providers.values())))

    def list_image_providers(self) -> List[str]:
        return [p.provider_name for p in self._image_providers.values()]

    def list_presentation_providers(self) -> List[str]:
        return [p.provider_name for p in self._presentation_providers.values()]


# Global singleton generation registry
generation_registry = GenerationRegistry()
