"""Gamma presentation provider implementation connecting to PresentationGenerationProvider interface."""

from typing import Optional
from backend.workline.generation.models import GeneratedPresentationArtifact, PresentationGenerationRequest
from backend.workline.generation.presentation.client import GammaClient
from backend.workline.generation.presentation.validation import PresentationValidator
from backend.workline.generation.registry import PresentationGenerationProvider


class GammaProvider(PresentationGenerationProvider):
    """Gamma slide deck and technical presentation generation provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = GammaClient(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Gamma"

    async def generate(self, request: PresentationGenerationRequest) -> GeneratedPresentationArtifact:
        """Render presentation deck artifact."""
        if not self.validate_request(request):
            raise ValueError(f"Invalid presentation request for provider '{self.provider_name}'")
        return await self.client.render_presentation(request)

    def validate_request(self, request: PresentationGenerationRequest) -> bool:
        """Validate request parameters."""
        is_valid, _ = PresentationValidator.validate_request(request)
        return is_valid

    async def get_status(self, request_id: str) -> str:
        """Query generation status."""
        return self.client.get_job_status(request_id)

    async def cancel(self, request_id: str) -> bool:
        """Cancel in-flight generation."""
        return self.client.cancel_job(request_id)

    async def get_result(self, request_id: str) -> Optional[GeneratedPresentationArtifact]:
        """Fetch completed presentation artifact."""
        return self.client.get_job_artifact(request_id)
