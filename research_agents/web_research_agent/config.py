"""
Configuration management for WebResearchAgent (Agent #2).
Reads environment settings for Tavily, Anakin, caching, and rate limiting.
"""

import os
from pydantic import BaseModel, Field


class WebResearchAgentConfig(BaseModel):
    """Configuration for WebResearchAgent, Tavily, and Anakin providers."""

    # Tavily Settings
    tavily_api_key: str = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY", "")
    )
    tavily_base_url: str = Field(
        default_factory=lambda: os.getenv("TAVILY_BASE_URL", "https://api.tavily.com")
    )
    tavily_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("TAVILY_TIMEOUT_SECONDS", "15.0"))
    )

    # Anakin Settings
    anakin_api_key: str = Field(
        default_factory=lambda: os.getenv("ANAKIN_API_KEY", "")
    )
    anakin_base_url: str = Field(
        default_factory=lambda: os.getenv("ANAKIN_BASE_URL", "https://api.anakin.ai/v1")
    )
    anakin_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("ANAKIN_TIMEOUT_SECONDS", "20.0"))
    )
    anakin_mcp_enabled: bool = Field(
        default_factory=lambda: os.getenv("ANAKIN_MCP_ENABLED", "false").lower()
        in ("true", "1", "yes")
    )

    # General Agent Parameters
    default_max_sources: int = Field(
        default_factory=lambda: int(os.getenv("WEB_RESEARCH_DEFAULT_MAX_SOURCES", "20"))
    )
    max_sources_cap: int = Field(
        default_factory=lambda: int(os.getenv("WEB_RESEARCH_MAX_SOURCES_CAP", "50"))
    )
    max_retries: int = Field(
        default_factory=lambda: int(os.getenv("WEB_RESEARCH_MAX_RETRIES", "3"))
    )

    # Cache Settings
    cache_enabled: bool = Field(
        default_factory=lambda: os.getenv("WEB_RESEARCH_CACHE_ENABLED", "true").lower()
        in ("true", "1", "yes")
    )
    cache_ttl_seconds: int = Field(
        default_factory=lambda: int(os.getenv("WEB_RESEARCH_CACHE_TTL", "3600"))
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("WEB_RESEARCH_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
web_research_config = WebResearchAgentConfig()
