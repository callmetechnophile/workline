"""
Abstract base class and exceptions for web research providers (Tavily, Anakin).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from research_agents.web_research_agent.schemas import RawWebResult


class ProviderError(Exception):
    """Base exception for web research provider errors."""

    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        code: str = "PROVIDER_ERROR",
        retryable: bool = False,
    ):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.code = code
        self.retryable = retryable


class ProviderAuthenticationError(ProviderError):
    """Raised when authentication credentials fail or are missing."""

    def __init__(self, provider: str, message: str = "Authentication failed."):
        super().__init__(
            message=message,
            provider=provider,
            code="PROVIDER_AUTH_ERROR",
            retryable=False,
        )


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded."""

    def __init__(self, provider: str, message: str = "Rate limit exceeded."):
        super().__init__(
            message=message,
            provider=provider,
            code="PROVIDER_RATE_LIMIT",
            retryable=True,
        )


class ProviderTimeoutError(ProviderError):
    """Raised when provider request times out."""

    def __init__(self, provider: str, message: str = "Provider request timed out."):
        super().__init__(
            message=message,
            provider=provider,
            code="PROVIDER_TIMEOUT",
            retryable=True,
        )


class ProviderUnavailableError(ProviderError):
    """Raised when provider service is unreachable."""

    def __init__(self, provider: str, message: str = "Provider service unreachable."):
        super().__init__(
            message=message,
            provider=provider,
            code="PROVIDER_UNAVAILABLE",
            retryable=True,
        )


class ExtractionError(ProviderError):
    """Raised when page extraction or parsing fails."""

    def __init__(self, provider: str, message: str = "Web extraction failed."):
        super().__init__(
            message=message,
            provider=provider,
            code="EXTRACTION_FAILURE",
            retryable=False,
        )


class InvalidURLError(ProviderError):
    """Raised when a supplied target URL is malformed or invalid."""

    def __init__(self, provider: str, message: str = "Supplied URL is invalid."):
        super().__init__(
            message=message,
            provider=provider,
            code="INVALID_URL",
            retryable=False,
        )


class WebResearchProvider(ABC):
    """Abstract interface for web search, scraping, and crawling providers."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        execution_id: Optional[str] = None,
    ) -> List[RawWebResult]:
        """Executes a web search query."""
        pass

    @abstractmethod
    async def extract(
        self,
        url: str,
        execution_id: Optional[str] = None,
    ) -> Optional[RawWebResult]:
        """Extracts content from a specific target URL."""
        pass

    @abstractmethod
    async def crawl(
        self,
        url: str,
        max_depth: int = 1,
        execution_id: Optional[str] = None,
    ) -> List[RawWebResult]:
        """Crawls linked pages starting from a base URL."""
        pass
