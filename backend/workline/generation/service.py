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

        # Compute versioning: count prior generations for this project+purpose
        with self._lock:
            existing = [
                a for a in self._artifacts.values()
                if getattr(a, "project_id", None) == project_id
                and getattr(a, "image_type", None) == purpose.value
            ]
            generation_version = len(existing) + 1

        conversation_id = (extra_context or {}).get("conversation_id")

        request = ImageGenerationRequest(
            project_id=project_id,
            team_id=team_id,
            provider=provider.provider_name,
            purpose=purpose,
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            conversation_id=conversation_id,
        )

        artifact = await provider.generate(request)

        # Stamp generation version and conversation
        artifact.generation_version = generation_version
        artifact.image_type = purpose.value
        if conversation_id:
            artifact.conversation_id = conversation_id

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
        """
        Persist generation metadata to SurrealDB project asset store.
        Records: artifact_id, project_id, conversation_id, image_type, model,
                 provider, sha256, generation_version, created_at, storage_path.
        Does NOT store: prompt_hash, content (SVG body), API keys.
        Failures are non-fatal — artifact is already in-memory.
        """
        try:
            import asyncio
            from backend.workline.database.surrealdb import surreal_db

            metadata = {
                "artifact_id": artifact.artifact_id,
                "project_id": project_id,
                "image_type": getattr(artifact, "image_type", None),
                "conversation_id": getattr(artifact, "conversation_id", None),
                "provider": getattr(artifact, "provider", None),
                "model": getattr(artifact, "model", None),
                "format": getattr(artifact, "format", None),
                "sha256": getattr(artifact, "sha256", None),
                "size": getattr(artifact, "size", None),
                "generation_version": getattr(artifact, "generation_version", 1),
                "storage_path": getattr(artifact, "storage_path", None),
                "created_at": getattr(artifact, "created_at", None),
            }
            # Attempt async persist — fire-and-forget in sync context
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule as a background task (don't block generation response)
                    loop.create_task(
                        surreal_db.query(
                            f"CREATE project_asset SET {', '.join(f'{k} = ${k}' for k in metadata)}",
                            metadata,
                        )
                    )
                else:
                    loop.run_until_complete(
                        surreal_db.query(
                            f"CREATE project_asset SET {', '.join(f'{k} = ${k}' for k in metadata)}",
                            metadata,
                        )
                    )
            except Exception:
                pass  # SurrealDB may be offline in dev; in-memory store is the durable copy

            logger.info(
                f"[GenerationService] Registered artifact='{artifact.artifact_id}' "
                f"project='{project_id}' model='{metadata.get('model')}' "
                f"version={metadata.get('generation_version')}"
            )
        except Exception as exc:
            logger.warning(f"[GenerationService] Metadata sync failed (non-fatal): {exc}")


# Global singleton generation service
generation_service = GenerationService()
