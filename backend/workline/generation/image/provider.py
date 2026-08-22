"""Paper Banana provider implementation connecting to the ImageGenerationProvider interface."""

from typing import Optional
from backend.workline.generation.image.client import PaperBananaClient
from backend.workline.generation.image.validation import ImageRequestValidator
from backend.workline.generation.models import GeneratedImageArtifact, ImageGenerationRequest
from backend.workline.generation.registry import ImageGenerationProvider


class PaperBananaProvider(ImageGenerationProvider):
    """Paper Banana technical visualization and engineering diagram provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = PaperBananaClient(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "PaperBanana"

    async def generate(self, request: ImageGenerationRequest) -> GeneratedImageArtifact:
        """Render technical visual artifact."""
        if not self.validate_request(request):
            raise ValueError(f"Invalid image generation request for provider '{self.provider_name}'")
        return await self.client.render_visual(request)

    def validate_request(self, request: ImageGenerationRequest) -> bool:
        """Validate request parameters."""
        is_valid, _ = ImageRequestValidator.validate(request)
        return is_valid

    async def get_status(self, request_id: str) -> str:
        """Query status of generation."""
        return self.client.get_job_status(request_id)

    async def cancel(self, request_id: str) -> bool:
        """Cancel in-flight generation."""
        return self.client.cancel_job(request_id)

    async def get_result(self, request_id: str) -> Optional[GeneratedImageArtifact]:
        """Fetch completed visual artifact."""
        return self.client.get_job_artifact(request_id)
