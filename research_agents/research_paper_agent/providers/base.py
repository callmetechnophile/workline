"""
Abstract base class and exceptions for research paper providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from research_agents.research_paper_agent.schemas import RawPaperRecord


class ProviderError(Exception):
    """Base exception for research paper provider errors."""

    def __init__(self, message: str, code: str = "PROVIDER_ERROR", retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable


class ProviderAuthenticationError(ProviderError):
    """Raised on invalid credentials or unauthorized access."""

    def __init__(self, message: str = "Authentication failed with research provider."):
        super().__init__(message=message, code="PROVIDER_AUTH_ERROR", retryable=False)


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded."""

    def __init__(self, message: str = "Provider rate limit exceeded. Please retry later."):
        super().__init__(message=message, code="PROVIDER_RATE_LIMIT", retryable=True)


class ProviderTimeoutError(ProviderError):
    """Raised when provider request times out."""

    def __init__(self, message: str = "Provider search request timed out."):
        super().__init__(message=message, code="PROVIDER_TIMEOUT", retryable=True)


class ProviderUnavailableError(ProviderError):
    """Raised when provider service is down or unreachable."""

    def __init__(self, message: str = "Provider service is temporarily unreachable."):
        super().__init__(message=message, code="PROVIDER_UNAVAILABLE", retryable=True)


class MalformedResponseError(ProviderError):
    """Raised when provider returns an unparseable response payload."""

    def __init__(self, message: str = "Provider returned a malformed response."):
        super().__init__(message=message, code="PROVIDER_MALFORMED_RESPONSE", retryable=False)


class BasePaperProvider(ABC):
    """Abstract interface for all research paper acquisition sources."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 20,
        execution_id: Optional[str] = None,
    ) -> List[RawPaperRecord]:
        """
        Executes a targeted search against the provider.

        Args:
            query: The search term or phrase.
            limit: Maximum raw candidates to request.
            execution_id: Optional tracking identifier for logging.

        Returns:
            List of RawPaperRecord objects.
        """
        pass
