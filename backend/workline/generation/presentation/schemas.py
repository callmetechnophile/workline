"""Schemas for Gamma presentation generation."""

from typing import List, Optional
from pydantic import BaseModel, Field
from backend.workline.generation.models import PresentationPurpose, SlideType


class PresentationTheme(BaseModel):
    """Visual theme settings for Gamma decks."""
    theme_name: str = "engineering_dark"
    primary_color: str = "#6366f1"
    background_color: str = "#09090b"
    font_family: str = "Inter"


class DeckMetadata(BaseModel):
    """Deck configuration options."""
    title: str
    audience: str
    purpose: PresentationPurpose
    aspect_ratio: str = "16:9"
    theme: PresentationTheme = Field(default_factory=PresentationTheme)
