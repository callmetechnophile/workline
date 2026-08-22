"""Pydantic-based project manifest schema and YAML serializer for Workline."""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseModel, Field, field_validator

from cli.wline.core.lifecycle import ProjectLifecycle, create_default_lifecycle


def normalize_project_name(raw_name: str) -> str:
    """
    Normalize a human-readable project name into a safe directory/identifier name.
    Example: "My Autonomous Solar-Powered Rover" -> "my-autonomous-solar-powered-rover"
    """
    if not raw_name or not raw_name.strip():
        return "untitled-project"

    # Replace non-alphanumeric chars with hyphens
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", raw_name.strip()).strip("-").lower()
    # Collapse multiple consecutive hyphens
    cleaned = re.sub(r"-+", "-", cleaned)
    return cleaned if cleaned else "untitled-project"


def parse_timeline_days(raw_input: str) -> int:
    """
    Parse a user timeline string into number of days.
    Examples:
        '8 weeks' -> 56
        '30 days' -> 30
        '2 months' -> 60
        '45' -> 45
    """
    if not raw_input:
        return 56

    val = raw_input.strip().lower()
    match = re.match(r"^(\d+(?:\.\d+)?)\s*(week|weeks|w|day|days|d|month|months|m)?$", val)
    if match:
        num = float(match.group(1))
        unit = match.group(2) or "days"
        if unit in ("week", "weeks", "w"):
            return int(num * 7)
        if unit in ("month", "months", "m"):
            return int(num * 30)
        return int(num)

    # Fallback default
    return 56


def parse_budget_amount(raw_input: str) -> float:
    """Parse budget input string into a float amount."""
    if not raw_input:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(raw_input))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


class BudgetConfig(BaseModel):
    """Budget configuration model."""
    amount: float = 0.0
    currency: str = "INR"


class TimelineConfig(BaseModel):
    """Timeline configuration model."""
    target_days: int = 56


class TargetPlatformConfig(BaseModel):
    """Hardware target platform configuration."""
    controller: str = "ESP32-S3"


class ProjectMetadata(BaseModel):
    """Project creation and update timestamps."""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProjectManifest(BaseModel):
    """Workline project manifest model (workline.yaml)."""
    name: str
    display_name: str
    description: str = ""
    version: str = "0.1.0"
    domain: str = "general"
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    timeline: TimelineConfig = Field(default_factory=TimelineConfig)
    complexity: str = "medium"
    target_platform: TargetPlatformConfig = Field(default_factory=TargetPlatformConfig)
    lifecycle: ProjectLifecycle = Field(default_factory=create_default_lifecycle)
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        norm = normalize_project_name(v)
        if not norm:
            raise ValueError("Project name must not be empty.")
        return norm


def load_manifest(file_path: Path) -> ProjectManifest:
    """Load and validate a workline.yaml manifest from disk."""
    if not file_path.exists():
        raise FileNotFoundError(f"Manifest not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML manifest content in {file_path}")

    return ProjectManifest.model_validate(data)


def save_manifest(manifest: ProjectManifest, file_path: Path) -> None:
    """Serialize and write a validated ProjectManifest to workline.yaml."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    manifest.metadata.updated_at = datetime.now(timezone.utc).isoformat()
    raw_dict = manifest.model_dump(mode="json")

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(raw_dict, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
