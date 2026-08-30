"""
Configuration management for DocumentProcessingAgent (Agent #3).
Controls chunk sizes, OCR character thresholds, fetch timeouts, and quality weights.
"""

import os
from pydantic import BaseModel, Field


class DocumentProcessingAgentConfig(BaseModel):
    """Configuration for DocumentProcessingAgent and parsers."""

    # Processing & Chunking Parameters
    max_chunk_tokens: int = Field(
        default_factory=lambda: int(os.getenv("DOC_MAX_CHUNK_TOKENS", "512"))
    )
    chunk_overlap_tokens: int = Field(
        default_factory=lambda: int(os.getenv("DOC_CHUNK_OVERLAP_TOKENS", "64"))
    )
    min_chunk_characters: int = Field(
        default_factory=lambda: int(os.getenv("DOC_MIN_CHUNK_CHARS", "50"))
    )

    # OCR Detection Thresholds
    min_extracted_chars_per_page: int = Field(
        default_factory=lambda: int(os.getenv("DOC_MIN_CHARS_PER_PAGE", "40"))
    )
    ocr_trigger_total_chars: int = Field(
        default_factory=lambda: int(os.getenv("DOC_OCR_TRIGGER_TOTAL_CHARS", "150"))
    )

    # Quality Scoring Thresholds
    min_acceptable_quality_score: float = Field(
        default_factory=lambda: float(os.getenv("DOC_MIN_QUALITY_SCORE", "0.30"))
    )

    # Fetch & Download Settings
    download_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("DOC_DOWNLOAD_TIMEOUT_SECONDS", "25.0"))
    )
    max_file_size_bytes: int = Field(
        default_factory=lambda: int(
            os.getenv("DOC_MAX_FILE_SIZE_BYTES", str(50 * 1024 * 1024))
        )  # 50 MB
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("DOC_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
doc_config = DocumentProcessingAgentConfig()
