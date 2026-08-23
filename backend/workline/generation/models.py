"""Core data models, enums, and schemas for Visual Generation (Paper Banana) and Presentation Generation (Gamma)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GenerationStatus(str, Enum):
    """Lifecycle status of a generation request."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ImagePurpose(str, Enum):
    """Technical visual purpose classification."""
    ARCHITECTURE = "ARCHITECTURE"
    ENGINEERING = "ENGINEERING"
    PCB = "PCB"
    WORKFLOW = "WORKFLOW"
    RESEARCH = "RESEARCH"
    PRESENTATION = "PRESENTATION"
    DOCUMENTATION = "DOCUMENTATION"
    OTHER = "OTHER"


class PresentationPurpose(str, Enum):
    """Presentation objective classification."""
    PROJECT_OVERVIEW = "PROJECT_OVERVIEW"
    TECHNICAL_DEEP_DIVE = "TECHNICAL_DEEP_DIVE"
    HACKATHON = "HACKATHON"
    RESEARCH = "RESEARCH"
    ENGINEERING_REVIEW = "ENGINEERING_REVIEW"
    DEMO = "DEMO"
    BUSINESS = "BUSINESS"
    PROGRESS_REPORT = "PROGRESS_REPORT"
    DOCUMENTATION = "DOCUMENTATION"


class SlideType(str, Enum):
    """Structured slide categories for presentation outlines."""
    TITLE = "TITLE"
    PROBLEM = "PROBLEM"
    SOLUTION = "SOLUTION"
    ARCHITECTURE = "ARCHITECTURE"
    WORKFLOW = "WORKFLOW"
    ENGINEERING = "ENGINEERING"
    DATA = "DATA"
    AI = "AI"
    PCB = "PCB"
    PROCUREMENT = "PROCUREMENT"
    VALIDATION = "VALIDATION"
    RESULTS = "RESULTS"
    DEMO = "DEMO"
    ROADMAP = "ROADMAP"
    TEAM = "TEAM"
    CONCLUSION = "CONCLUSION"


class SlideContent(BaseModel):
    """Individual slide specification within a presentation outline."""
    slide_id: str = Field(default_factory=lambda: f"slide_{uuid.uuid4().hex[:6]}")
    slide_type: SlideType = SlideType.TITLE
    title: str
    objective: str
    key_points: List[str] = Field(default_factory=list)
    source_objects: List[str] = Field(default_factory=list, description="Provenance source identifiers")
    visual_requirements: Optional[str] = None
    speaker_notes: Optional[str] = None


class PresentationOutline(BaseModel):
    """Structured outline before presentation rendering."""
    outline_id: str = Field(default_factory=lambda: f"out_{uuid.uuid4().hex[:8]}")
    title: str
    subtitle: Optional[str] = None
    purpose: PresentationPurpose = PresentationPurpose.PROJECT_OVERVIEW
    audience: str = "Technical Audience"
    slides: List[SlideContent] = Field(default_factory=list)


class ImageGenerationRequest(BaseModel):
    """Request for generating technical visualizations."""
    request_id: str = Field(default_factory=lambda: f"img_req_{uuid.uuid4().hex[:8]}")
    project_id: str
    team_id: str = "default_team"
    provider: str = "PaperBanana"
    purpose: ImagePurpose = ImagePurpose.ARCHITECTURE
    prompt: str
    style: str = "technical_diagram"
    aspect_ratio: str = "16:9"
    reference_artifacts: List[str] = Field(default_factory=list)
    output_format: str = "svg"
    extra_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Project or session context")
    conversation_id: Optional[str] = Field(default=None, description="Conversation this image is attached to")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PresentationGenerationRequest(BaseModel):
    """Request for generating technical presentations."""
    request_id: str = Field(default_factory=lambda: f"pres_req_{uuid.uuid4().hex[:8]}")
    project_id: str
    team_id: str = "default_team"
    provider: str = "Gamma"
    title: str
    purpose: PresentationPurpose = PresentationPurpose.PROJECT_OVERVIEW
    audience: str = "Technical Audience"
    source_sections: List[str] = Field(default_factory=list)
    visual_requirements: Optional[str] = None
    slide_count: int = 10
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GeneratedImageArtifact(BaseModel):
    """Metadata record for a generated visual artifact."""
    artifact_id: str = Field(default_factory=lambda: f"art_img_{uuid.uuid4().hex[:8]}")
    project_id: str
    request_id: str
    image_type: str = "ARCHITECTURE"
    filename: str
    format: str
    width: int = 1920
    height: int = 1080
    size: int = 0
    sha256: str
    provider: str = "PaperBanana"
    model: str = "gemini-2.0-flash"
    prompt_hash: str
    content: Optional[str] = None  # SVG markup or data URI
    storage_path: Optional[str] = None  # Filesystem path on R2
    conversation_id: Optional[str] = None  # Conversation this image is attached to
    generation_version: int = 1  # Increments for each generation within same project+type
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_project_version: Optional[str] = None
    source_git_commit: Optional[str] = None


class GeneratedPresentationArtifact(BaseModel):
    """Metadata record for a generated presentation artifact."""
    artifact_id: str = Field(default_factory=lambda: f"art_pres_{uuid.uuid4().hex[:8]}")
    project_id: str
    request_id: str
    title: str
    filename: str
    format: str = "markdown"  # markdown deck or JSON
    slide_count: int
    size: int = 0
    sha256: str
    provider: str = "Gamma"
    model: str = "gamma-v2"
    outline: Optional[PresentationOutline] = None
    content: Optional[str] = None  # Full rendered markdown presentation
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_project_version: Optional[str] = None
    source_git_commit: Optional[str] = None
