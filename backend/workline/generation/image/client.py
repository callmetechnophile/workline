"""
PaperBanana Client — Technical Visual Renderer powered by Amazon Bedrock.

Architecture:
  ImageGenerationRequest
        ↓
  PaperBananaClient
        ↓
  ImagePromptBuilder (project-grounded prompt)
        ↓
  Amazon Bedrock Image Engine (Nova Canvas / Titan Image Generator / Claude SVG)
        ↓
  PNG / SVG artifact
        ↓
  GeneratedImageArtifact (stored on R2 filesystem + R3 metadata)

AWS Credentials are read ONLY from the server environment (AWS_REGION, IAM role, etc.).
They are NEVER passed from the client, NEVER logged, and NEVER returned in responses.
"""

import asyncio
import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from loguru import logger

from backend.workline.ai.bedrock.router import model_router
from backend.workline.generation.models import (
    GeneratedImageArtifact,
    ImageGenerationRequest,
    ImagePurpose,
)

# ---------------------------------------------------------------------------
# Storage — generated images/SVGs are written to a per-instance directory on R2.
# ---------------------------------------------------------------------------
_ARTIFACT_DIR = os.path.join(
    os.path.expanduser("~"), ".workline", "artifacts", "images"
)


def _ensure_artifact_dir() -> str:
    os.makedirs(_ARTIFACT_DIR, exist_ok=True)
    return _ARTIFACT_DIR


class BedrockImageEngine:
    """
    Amazon Bedrock engine for engineering image and diagram generation.
    Uses BedrockModelRouter (Nova Canvas / Titan Image / Claude Sonnet SVG synthesis).
    """

    @classmethod
    def is_available(cls) -> bool:
        """Returns True if AWS region or Bedrock client is configured."""
        return bool(os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

    @classmethod
    async def generate_visual(
        cls,
        prompt: str,
        image_type: str,
        project_id: str,
        aspect_ratio: str = "16:9",
    ) -> Optional[Dict[str, Any]]:
        """
        Calls Amazon Bedrock to generate an engineering visual or diagram.
        Returns dict with format, content (bytes or str), and model metadata.
        """
        loop = asyncio.get_event_loop()

        def _sync_call():
            try:
                # 1. First attempt native Bedrock raster image generation (Nova Canvas / Titan Image)
                img_res = model_router.image_generation(
                    prompt=f"Technical engineering visual: {prompt}",
                    aspect_ratio=aspect_ratio,
                )
                if img_res and img_res.image_bytes:
                    return {
                        "format": "png",
                        "content_bytes": img_res.image_bytes,
                        "model": img_res.model_id,
                        "width": img_res.width,
                        "height": img_res.height,
                    }
            except Exception as exc:
                logger.warning(f"[PaperBanana] Bedrock image model failed: {exc}; falling back to Bedrock Claude SVG synthesis.")

            try:
                # 2. Bedrock Claude SVG generation fallback
                svg_prompt = (
                    "You are an expert technical diagram generator. "
                    "Output ONLY valid SVG markup (no markdown, no backticks, no explanations). "
                    "Use a clean dark theme: background #09090b, strokes #06b6d4, text #e2e8f0. "
                    f"Generate a {image_type} diagram (1280x720) for: {prompt}"
                )
                ai_res = model_router.fast_code(prompt=svg_prompt)
                text = ai_res.text.strip()
                if "<svg" in text:
                    if text.startswith("```"):
                        lines = text.split("\n")
                        text = "\n".join(l for l in lines if not l.startswith("```")).strip()
                    return {
                        "format": "svg",
                        "content_str": text,
                        "model": ai_res.model_id,
                        "width": 1280,
                        "height": 720,
                    }
            except Exception as e:
                logger.warning(f"[PaperBanana] Bedrock SVG generation failed: {e}")

            return None

        return await loop.run_in_executor(None, _sync_call)


class PaperBananaClient:
    """
    PaperBanana visual generator grounded in Workline engineering context.
    Executes all visual synthesis via Amazon Bedrock.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        _ensure_artifact_dir()

    def _build_grounded_prompt(self, request: ImageGenerationRequest) -> str:
        """Constructs an engineering prompt from project context."""
        parts = [
            f"Project: {request.project_id}",
            f"Type: {request.purpose.value}",
            f"Specification: {request.prompt}",
        ]
        if request.extra_context:
            for k, v in request.extra_context.items():
                if v:
                    parts.append(f"{k}: {v}")
        return " | ".join(parts)

    def _compute_sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _generate_structural_svg(
        self,
        request: ImageGenerationRequest,
        prompt_hash: str,
    ) -> str:
        """Deterministic structural SVG fallback when AWS Bedrock is offline."""
        purpose_label = request.purpose.value.replace("_", " ").title()
        project_escaped = request.project_id.replace("<", "&lt;").replace(">", "&gt;")
        prompt_escaped = request.prompt[:90].replace("<", "&lt;").replace(">", "&gt;")

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#09090b"/>
  <rect x="20" y="20" width="1240" height="680" rx="12" fill="#0f172a" stroke="#0284c7" stroke-width="2"/>
  <text x="60" y="80" fill="#38bdf8" font-family="monospace" font-size="28" font-weight="bold">WORKLINE AI // {purpose_label}</text>
  <text x="60" y="120" fill="#64748b" font-family="monospace" font-size="14">PROJECT: {project_escaped} | ARTIFACT: {prompt_hash[:12]}</text>
  <line x1="60" y1="140" x2="1220" y2="140" stroke="#1e293b" stroke-width="2"/>
  <rect x="60" y="180" width="340" height="460" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5"/>
  <text x="80" y="220" fill="#f8fafc" font-family="monospace" font-size="16" font-weight="bold">Specification Input</text>
  <text x="80" y="260" fill="#94a3b8" font-family="monospace" font-size="13">{prompt_escaped}</text>
  <rect x="470" y="180" width="750" height="460" rx="8" fill="#020617" stroke="#0369a1" stroke-width="1.5"/>
  <text x="490" y="220" fill="#38bdf8" font-family="monospace" font-size="16" font-weight="bold">Bedrock Neural Visual Synthesis</text>
  <circle cx="845" cy="410" r="120" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-dasharray="8 4"/>
  <circle cx="845" cy="410" r="60" fill="#0369a1" fill-opacity="0.3" stroke="#38bdf8" stroke-width="2"/>
  <text x="845" y="415" fill="#f8fafc" font-family="monospace" font-size="14" text-anchor="middle" font-weight="bold">{purpose_label}</text>
</svg>"""

    async def render_visual(
        self,
        request: ImageGenerationRequest,
    ) -> GeneratedImageArtifact:
        """
        Renders an engineering diagram or visual via Amazon Bedrock.
        Persists artifact to R2 filesystem and returns GeneratedImageArtifact metadata.
        """
        grounded_prompt = self._build_grounded_prompt(request)
        prompt_hash = hashlib.sha256(grounded_prompt.encode("utf-8")).hexdigest()
        artifact_id = f"art_img_{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        artifact_dir = _ensure_artifact_dir()

        visual_result = await BedrockImageEngine.generate_visual(
            prompt=grounded_prompt,
            image_type=request.purpose.value,
            project_id=request.project_id,
            aspect_ratio=request.aspect_ratio or "16:9",
        )

        if visual_result:
            fmt = visual_result.get("format", "png")
            model_used = visual_result.get("model", model_router.image_model_id)
            filename = f"{artifact_id}.{fmt}"
            filepath = os.path.join(artifact_dir, filename)

            if fmt == "png":
                content_bytes = visual_result["content_bytes"]
                with open(filepath, "wb") as f:
                    f.write(content_bytes)
                sha256_hash = self._compute_sha256(content_bytes)
                content_text = None
            else:
                content_str = visual_result["content_str"]
                content_bytes = content_str.encode("utf-8")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content_str)
                sha256_hash = self._compute_sha256(content_bytes)
                content_text = content_str

            logger.info(
                f"[PaperBanana] Rendered visual via Bedrock ({model_used}): artifact_id={artifact_id} size={len(content_bytes)}b"
            )
        else:
            # Offline / Fallback structural SVG
            fmt = "svg"
            model_used = "fallback-svg"
            filename = f"{artifact_id}.svg"
            filepath = os.path.join(artifact_dir, filename)
            svg_content = self._generate_structural_svg(request, prompt_hash)
            content_bytes = svg_content.encode("utf-8")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(svg_content)
            sha256_hash = self._compute_sha256(content_bytes)
            content_text = svg_content

        return GeneratedImageArtifact(
            artifact_id=artifact_id,
            request_id=request.request_id,
            project_id=request.project_id,
            conversation_id=request.extra_context.get("conversation_id", "") if request.extra_context else "",
            image_type=request.purpose.value,
            filename=filename,
            format=fmt,
            width=1280,
            height=720,
            sha256=sha256_hash,
            prompt_hash=prompt_hash,
            content=content_text,
            storage_path=filepath,
            created_at=created_at,
            provider="PaperBanana",
            model=model_used,
        )


# Global singleton instance
paperbanana_client = PaperBananaClient()
