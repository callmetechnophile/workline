"""Gamma presentation generation module."""

from backend.workline.generation.presentation.client import GammaClient
from backend.workline.generation.presentation.prompts import PresentationContextBuilder
from backend.workline.generation.presentation.provider import GammaProvider
from backend.workline.generation.presentation.schemas import DeckMetadata, PresentationTheme
from backend.workline.generation.presentation.validation import PresentationValidator

__all__ = [
    "GammaProvider",
    "GammaClient",
    "PresentationContextBuilder",
    "PresentationValidator",
    "DeckMetadata",
    "PresentationTheme",
]
