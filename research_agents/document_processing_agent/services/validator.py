"""
Document source validator, remote fetcher, and format detector for DocumentProcessingAgent.
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import httpx
from loguru import logger

from research_agents.document_processing_agent.config import doc_config
from research_agents.document_processing_agent.parsers.base import (
    CorruptedDocumentError,
    ParserError,
    UnsupportedFormatError,
)
from research_agents.document_processing_agent.schemas import DocumentProcessingInput, DocumentTypeLiteral


class DocumentValidator:
    """Validates input paths/URLs, fetches remote documents, and detects document format."""

    @staticmethod
    def detect_format(
        content_bytes: bytes,
        source_url: Optional[str] = None,
        local_path: Optional[str] = None,
        declared_type: DocumentTypeLiteral = "auto",
    ) -> DocumentTypeLiteral:
        """Determines format type ('pdf', 'html', 'text') based on magic bytes and extensions."""
        if declared_type in ("pdf", "html", "text"):
            return declared_type

        # 1. Magic bytes detection
        if content_bytes.startswith(b"%PDF-"):
            return "pdf"
        if content_bytes.strip().startswith(b"<!DOCTYPE html") or content_bytes.strip().startswith(b"<html") or b"<body" in content_bytes[:1000]:
            return "html"

        # 2. File extension detection
        path_or_url = (local_path or source_url or "").lower()
        if path_or_url.endswith(".pdf"):
            return "pdf"
        if path_or_url.endswith(".html") or path_or_url.endswith(".htm"):
            return "html"
        if path_or_url.endswith(".txt") or path_or_url.endswith(".md"):
            return "text"

        # Default fallback to text if valid UTF-8
        return "text"

    async def fetch_document(self, input_data: DocumentProcessingInput) -> Tuple[bytes, DocumentTypeLiteral]:
        """
        Fetches document bytes from local filesystem or remote URL, and detects document type.
        """
        content_bytes: Optional[bytes] = None

        # 1. Local path loading
        if input_data.local_path:
            local_p = Path(input_data.local_path)
            if not local_p.exists() or not local_p.is_file():
                raise ParserError(f"Local file does not exist: {input_data.local_path}", code="FILE_NOT_FOUND")
            try:
                content_bytes = local_p.read_bytes()
            except Exception as e:
                raise CorruptedDocumentError(f"Failed to read local document: {str(e)}")

        # 2. Remote URL download
        elif input_data.source_url:
            url = input_data.source_url.strip()
            if not (url.startswith("http://") or url.startswith("https://")):
                raise ParserError(f"Invalid remote document URL: {url}", code="INVALID_URL")

            try:
                async with httpx.AsyncClient(timeout=doc_config.download_timeout_seconds, follow_redirects=True) as client:
                    res = await client.get(url)
                    if res.status_code != 200:
                        raise ParserError(
                            f"Failed to download remote document (HTTP {res.status_code}): {url}",
                            code="DOWNLOAD_FAILED",
                            retryable=(res.status_code >= 500 or res.status_code == 429),
                        )
                    content_bytes = res.content
            except httpx.TimeoutException:
                raise ParserError(f"Download timed out for URL: {url}", code="DOWNLOAD_TIMEOUT", retryable=True)
            except httpx.RequestError as req_err:
                raise ParserError(f"Network error downloading document: {str(req_err)}", code="NETWORK_ERROR", retryable=True)

        if not content_bytes:
            raise CorruptedDocumentError("Retrieved document content is empty.")

        if len(content_bytes) > doc_config.max_file_size_bytes:
            raise ParserError(
                f"Document exceeds maximum allowed size ({len(content_bytes)} > {doc_config.max_file_size_bytes} bytes).",
                code="FILE_TOO_LARGE",
            )

        detected_type = self.detect_format(
            content_bytes=content_bytes,
            source_url=input_data.source_url,
            local_path=input_data.local_path,
            declared_type=input_data.document_type,
        )

        return content_bytes, detected_type
