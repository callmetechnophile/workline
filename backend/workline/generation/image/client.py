"""Paper Banana API client and technical visual renderer."""

import asyncio
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.workline.generation.models import GeneratedImageArtifact, ImageGenerationRequest, ImagePurpose


class PaperBananaClient:
    """Client for rendering technical visualizations via Paper Banana."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._jobs: Dict[str, Dict[str, Any]] = {}

    async def render_visual(self, request: ImageGenerationRequest) -> GeneratedImageArtifact:
        """Render a technical visual artifact matching the request specification."""
        self._jobs[request.request_id] = {"status": "PROCESSING"}
        await asyncio.sleep(0.05)  # Simulate network / engine processing

        prompt_hash = hashlib.sha256(request.prompt.encode("utf-8")).hexdigest()
        artifact_id = f"art_img_{uuid.uuid4().hex[:8]}"

        # Render technical vector graphic (SVG)
        svg_content = self._generate_technical_svg(request)
        output_hash = hashlib.sha256(svg_content.encode("utf-8")).hexdigest()

        artifact = GeneratedImageArtifact(
            artifact_id=artifact_id,
            project_id=request.project_id,
            request_id=request.request_id,
            filename=f"{request.project_id}_{request.purpose.value.lower()}_{artifact_id}.svg",
            format="svg",
            width=1920,
            height=1080,
            size=len(svg_content.encode("utf-8")),
            sha256=output_hash,
            provider="PaperBanana",
            model="paper-banana-v1",
            prompt_hash=prompt_hash,
            content=svg_content,
        )

        self._jobs[request.request_id] = {"status": "COMPLETED", "artifact": artifact}
        return artifact

    def get_job_status(self, request_id: str) -> str:
        """Query job status."""
        return self._jobs.get(request_id, {}).get("status", "UNKNOWN")

    def cancel_job(self, request_id: str) -> bool:
        """Cancel an in-flight job."""
        if request_id in self._jobs:
            self._jobs[request_id]["status"] = "CANCELLED"
            return True
        return False

    def get_job_artifact(self, request_id: str) -> Optional[GeneratedImageArtifact]:
        """Fetch completed artifact."""
        return self._jobs.get(request_id, {}).get("artifact")

    def _generate_technical_svg(self, request: ImageGenerationRequest) -> str:
        """Generate a clean dark-mode technical SVG diagram."""
        title = f"WORKLINE: {request.purpose.value} [{request.project_id}]"
        
        if request.purpose == ImagePurpose.PCB:
            return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <rect width="1920" height="1080" fill="#09090b"/>
  <rect x="200" y="150" width="1520" height="780" rx="16" fill="#064e3b" stroke="#10b981" stroke-width="4"/>
  <text x="240" y="210" fill="#a7f3d0" font-family="monospace" font-size="28" font-weight="bold">{title}</text>
  <rect x="400" y="300" width="300" height="300" rx="8" fill="#18181b" stroke="#3b82f6" stroke-width="3"/>
  <text x="450" y="460" fill="#60a5fa" font-family="sans-serif" font-size="24">MCU (LQFP-64)</text>
  <rect x="900" y="300" width="220" height="180" rx="8" fill="#18181b" stroke="#f59e0b" stroke-width="3"/>
  <text x="930" y="400" fill="#fbbf24" font-family="sans-serif" font-size="22">Step-Down Reg</text>
  <circle cx="1010" cy="390" r="140" fill="url(#thermalGradient)" opacity="0.35"/>
  <defs>
    <radialGradient id="thermalGradient">
      <stop offset="0%" stop-color="#ef4444" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
    </radialGradient>
  </defs>
</svg>"""

        # Default Architecture / Engineering SVG
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <rect width="1920" height="1080" fill="#09090b"/>
  <text x="100" y="80" fill="#818cf8" font-family="monospace" font-size="32" font-weight="bold">{title}</text>
  <rect x="100" y="140" width="1720" height="140" rx="12" fill="#18181b" stroke="#6366f1" stroke-width="2"/>
  <text x="140" y="220" fill="#e0e7ff" font-family="sans-serif" font-size="24" font-weight="bold">USER INTERFACES: Workline CLI (wline) + Next.js 16 Client (TypeScript 7)</text>
  <rect x="100" y="320" width="1720" height="180" rx="12" fill="#18181b" stroke="#10b981" stroke-width="2"/>
  <text x="140" y="400" fill="#d1fae5" font-family="sans-serif" font-size="24" font-weight="bold">MULTI-AGENT ENGINE: Google ADK Orchestrator (Planning, Research, Builder Trees)</text>
  <rect x="100" y="540" width="840" height="200" rx="12" fill="#18181b" stroke="#38bdf8" stroke-width="2"/>
  <text x="140" y="620" fill="#bae6fd" font-family="sans-serif" font-size="22" font-weight="bold">INTEROPERABILITY GATEWAY: Bindu A2A + Corsair</text>
  <rect x="980" y="540" width="840" height="200" rx="12" fill="#18181b" stroke="#f59e0b" stroke-width="2"/>
  <text x="1020" y="620" fill="#fef3c7" font-family="sans-serif" font-size="22" font-weight="bold">HARDWARE & PHYSICS: PCB Unit, PINN Thermal, BOM, x402</text>
  <rect x="100" y="780" width="1720" height="180" rx="12" fill="#18181b" stroke="#a855f7" stroke-width="2"/>
  <text x="140" y="860" fill="#f3e8ff" font-family="sans-serif" font-size="24" font-weight="bold">DATA STORES & INFRA: SurrealDB Graph + Qdrant Vector + Git/GitHub + Podman</text>
</svg>"""
