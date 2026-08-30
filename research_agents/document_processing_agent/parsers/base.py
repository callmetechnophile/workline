"""
Abstract base class and exceptions for document parsers (PDF, HTML, Text).
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    ExtractedBlock,
    ExtractedFigure,
    ExtractedLink,
    ExtractedReference,
    ExtractedTable,
)


class ParserError(Exception):
    """Base exception for document parsing failures."""

    def __init__(self, message: str, code: str = "PARSER_ERROR", retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable


class UnsupportedFormatError(ParserError):
    """Raised when the document file format is unsupported."""

    def __init__(self, message: str = "Unsupported document format."):
        super().__init__(message=message, code="UNSUPPORTED_FORMAT", retryable=False)


class CorruptedDocumentError(ParserError):
    """Raised when the document binary is corrupted or unreadable."""

    def __init__(self, message: str = "Document is corrupted or cannot be opened."):
        super().__init__(message=message, code="CORRUPTED_DOCUMENT", retryable=False)


class BaseDocumentParser(ABC):
    """Abstract interface for format-specific document parsers."""

    @abstractmethod
    def parse(
        self,
        content_bytes: bytes,
        source_url: Optional[str] = None,
        title_hint: Optional[str] = None,
    ) -> Tuple[
        DocumentMetadata,
        List[ExtractedBlock],
        List[ExtractedTable],
        List[ExtractedFigure],
        List[ExtractedLink],
        List[ExtractedReference],
    ]:
        """
        Parses document binary content into structured components.

        Returns:
            (metadata, blocks, tables, figures, links, references)
        """
        pass
