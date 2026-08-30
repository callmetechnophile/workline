"""
Configuration management for ResearchPaperAgent (Agent #1).
Reads environment variables for Freephdlabor and execution parameters.
"""

import os
from pydantic import BaseModel, Field


class ResearchPaperAgentConfig(BaseModel):
    """Configuration for ResearchPaperAgent and Freephdlabor provider."""

    # Freephdlabor Provider Settings
    freephdlabor_api_key: str = Field(
        default_factory=lambda: os.getenv("FREEPHDLABOR_API_KEY", "")
    )
    freephdlabor_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "FREEPHDLABOR_BASE_URL", "https://api.freephdlabor.com/v1"
        )
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(
            os.getenv("FREEPHDLABOR_TIMEOUT_SECONDS", "15.0")
        )
    )
    max_retries: int = Field(
        default_factory=lambda: int(os.getenv("FREEPHDLABOR_MAX_RETRIES", "3"))
    )

    # Retrieval and Scoring Parameters
    default_max_papers: int = Field(
        default_factory=lambda: int(os.getenv("RESEARCH_DEFAULT_MAX_PAPERS", "20"))
    )
    max_papers_cap: int = Field(
        default_factory=lambda: int(os.getenv("RESEARCH_MAX_PAPERS_CAP", "50"))
    )
    min_relevance_threshold: float = Field(
        default_factory=lambda: float(
            os.getenv("RESEARCH_MIN_RELEVANCE_THRESHOLD", "0.20")
        )
    )

    # Cache Settings
    cache_enabled: bool = Field(
        default_factory=lambda: os.getenv("RESEARCH_CACHE_ENABLED", "true").lower()
        in ("true", "1", "yes")
    )
    cache_ttl_seconds: int = Field(
        default_factory=lambda: int(os.getenv("RESEARCH_CACHE_TTL", "3600"))
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("RESEARCH_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
research_config = ResearchPaperAgentConfig()
