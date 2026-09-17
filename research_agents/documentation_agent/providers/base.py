"""
Abstract base class for the LLM prose generation provider.
LLM generates prose ONLY — deterministic code controls all metadata.
"""
from abc import ABC, abstractmethod
from typing import Dict


class BaseDocProvider(ABC):

    @abstractmethod
    def generate_section(self, section_name: str, context: Dict) -> str:
        """Generate a prose section given a structured context dict."""
        ...

    @abstractmethod
    def summarize_changes(self, old_text: str, new_text: str) -> str:
        """Produce a human-readable change summary between two text versions."""
        ...
