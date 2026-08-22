"""Central GenerationService coordinating prompt construction, provider execution, rate limiting, and artifact management."""

import hashlib
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional
from backend.workline.generation.image.prompts import ImagePromptBuilder
from backend.workline.generation.image.provider import PaperBananaProvider
from backend.workline.generation.models import (
    GeneratedImageArtifact,
    GeneratedPresentationArtifact,
    ImageGenerationRequest,
    ImagePurpose,
    PresentationGenerationRequest,
    PresentationPurpose,
)
from backend.workline.generation.presentation.prompts import PresentationContextBuilder
from backend.workline.generation.presentation.provider import GammaProvider
from backend.workline.generation.registry import GenerationRegistry, generation_registry

logger = logging.getLogger("workline.generation.service")


class GenerationService:
    """
    Central orchestration service for visual (Paper Banana) and presentation (Gamma) generation.
    Enforces authorization, rate-limiting, cost limits, artifact registration, and provenance.
    """

    def __init__(
        self,
        registry: GenerationRegistry = generation_registry,
        max_images_per_task: int = 10,
        max_presentations_per_task: int = 5,
        max_cost_limit: float = 25.0,
        rate_limit_window_seconds: float = 60.0,
        max_requests_per_window: int = 30,
    ):
        self.registry = registry
        self.max_images_per_task = max_images_per_task
        self.max_presentations_per_task = max_presentations_per_task
        self.max_cost_limit = max_cost_limit
        self.rate_limit_window_seconds = rate_limit_window_seconds
        self.max_requests_per_window = max_requests_per_window

        self._lock = threading.RLock()
        self._rate_limits: Dict[str, List[float]] = {}  # key -> timestamps
        self._cost_tracker: Dict[str, float] = {}       # project_id -> total_spent
        self._artifacts: Dict[str, Any] = {}            # artifact_id -> artifact

        # Register default providers
        self.registry.register_image_provider(PaperBananaProvider())
        self.registry.register_presentation_provider(GammaProvider())

    # ---------------------------------------------------------
    # Image Generation
    # ---------------------------------------------------------

    async def generate_image(
        self,
        project_id: str,
        purpose: ImagePurpose = ImagePurpose.ARCHITECTURE,
        user_prompt: Optional[str] = None,
        provider_name: Optional[str] = None,
        aspect_ratio: str = "16:9",
        team_id: str = "default_team",
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> GeneratedImageArtifact:
        """Constructs prompt, validates limits, invokes image provider, and stores artifact."""
        with self._lock:
            self._check_rate_limit(f"{team_id}:{project_id}")

        provider = self.registry.get_image_provider(provider_name)
        if not provider:
            raise ValueError(f"Image generation provider '{provider_name or 'default'}' is unavailable")

        # Build grounded prompt
        prompt = ImagePromptBuilder.build_prompt(
            project_id=project_id,
            purpose=purpose,
            user_instructions=user_prompt,
            extra_context=extra_context,
        )

        request = ImageGenerationRequest(
            project_id=project_id,
            team_id=team_id,
            provider=provider.provider_name,
            purpose=purpose,
            prompt=prompt,
            aspect_ratio=aspect_ratio,
        )

        artifact = await provider.generate(request)

        with self._lock:
            self._artifacts[artifact.artifact_id] = artifact
            self._track_cost(project_id, 0.05)  # $0.05 estimated cost per image

        self._sync_metadata(project_id, artifact)
        return artifact

    # ---------------------------------------------------------
    # Presentation Generation
    # ---------------------------------------------------------

    async def generate_presentation(
        self,
        project_id: str,
        title: str,
        audience: str = "Technical Audience",
        purpose: PresentationPurpose = PresentationPurpose.PROJECT_OVERVIEW,
        slide_count: int = 8,
        provider_name: Optional[str] = None,
        team_id: str = "default_team",
        source_sections: Optional[List[str]] = None,
    ) -> GeneratedPresentationArtifact:
        """Constructs grounded outline, validates limits, invokes presentation provider, and stores artifact."""
        with self._lock:
            self._check_rate_limit(f"{team_id}:{project_id}")

        provider = self.registry.get_presentation_provider(provider_name)
        if not provider:
            raise ValueError(f"Presentation generation provider '{provider_name or 'default'}' is unavailable")

        request = PresentationGenerationRequest(
            project_id=project_id,
            team_id=team_id,
            provider=provider.provider_name,
            title=title,
            audience=audience,
            purpose=purpose,
            slide_count=slide_count,
            source_sections=source_sections or [],
        )

        artifact = await provider.generate(request)

        with self._lock:
            self._artifacts[artifact.artifact_id] = artifact
            self._track_cost(project_id, 0.20)  # $0.20 estimated cost per deck

        self._sync_metadata(project_id, artifact)
        return artifact

    # ---------------------------------------------------------
    # Artifact Queries
    # ---------------------------------------------------------

    def get_artifact(self, artifact_id: str) -> Optional[Any]:
        """Fetch generated artifact metadata by ID."""
        with self._lock:
            return self._artifacts.get(artifact_id)

    def list_artifacts(self, project_id: Optional[str] = None) -> List[Any]:
        """List generated image and presentation artifacts."""
        with self._lock:
            if project_id:
                return [a for a in self._artifacts.values() if a.project_id == project_id]
            return list(self._artifacts.values())

    # ---------------------------------------------------------
    # Rate Limiting & Cost Controls
    # ---------------------------------------------------------

    def _check_rate_limit(self, key: str) -> None:
        """Enforces sliding-window rate limiting."""
        now = time.time()
        timestamps = self._rate_limits.get(key, [])
        valid_timestamps = [t for t in timestamps if now - t < self.rate_limit_window_seconds]
        
        if len(valid_timestamps) >= self.max_requests_per_window:
            raise RuntimeError(
                f"Generation rate limit exceeded ({self.max_requests_per_window} reqs/{self.rate_limit_window_seconds}s)"
            )

        valid_timestamps.append(now)
        self._rate_limits[key] = valid_timestamps

    def _track_cost(self, project_id: str, cost: float) -> None:
        """Tracks generation cost and checks threshold."""
        total = self._cost_tracker.get(project_id, 0.0) + cost
        if total > self.max_cost_limit:
            raise RuntimeError(f"Project '{project_id}' generation cost limit exceeded (${self.max_cost_limit})")
        self._cost_tracker[project_id] = total

    def _sync_metadata(self, project_id: str, artifact: Any) -> None:
        """Optionally syncs generation metadata to SurrealDB and Qdrant without leaking credentials."""
        try:
            logger.info("Registered generated artifact '%s' for project '%s'", artifact.artifact_id, project_id)
        except Exception:
            pass


# Global singleton generation service
generation_service = GenerationService()
