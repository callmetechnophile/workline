"""Document parsers for PDF, HTML, and plain text."""

from research_agents.document_processing_agent.parsers.base import (
    BaseDocumentParser,
    CorruptedDocumentError,
    ParserError,
    UnsupportedFormatError,
)
from research_agents.document_processing_agent.parsers.html_parser import HTMLDocumentParser
from research_agents.document_processing_agent.parsers.pdf_parser import PDFDocumentParser
from research_agents.document_processing_agent.parsers.text_parser import TextDocumentParser

__all__ = [
    "BaseDocumentParser",
    "PDFDocumentParser",
    "HTMLDocumentParser",
    "TextDocumentParser",
    "ParserError",
    "CorruptedDocumentError",
    "UnsupportedFormatError",
]
