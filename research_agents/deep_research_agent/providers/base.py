"""
Abstract reasoning provider interface and structured exceptions for DeepResearchAgent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ProviderError(Exception):
    """Base exception for reasoning provider errors."""

    def __init__(self, provider: str, message: str, code: str = "PROVIDER_ERROR", retryable: bool = False):
        super().__init__(message)
        self.provider = provider
        self.message = message
        self.code = code
        self.retryable = retryable


class ProviderAuthenticationError(ProviderError):
    """Raised when AWS / API credentials are invalid or missing."""

    def __init__(self, provider: str, message: str = "AWS / API Authentication failed."):
        super().__init__(provider=provider, message=message, code="AUTH_FAILED", retryable=False)


class ProviderRateLimitError(ProviderError):
    """Raised when Bedrock quota or TPS rate limit is exceeded."""

    def __init__(self, provider: str, message: str = "Rate limit / quota exceeded."):
        super().__init__(provider=provider, message=message, code="RATE_LIMIT_EXCEEDED", retryable=True)


class ProviderTimeoutError(ProviderError):
    """Raised when reasoning request times out."""

    def __init__(self, provider: str, message: str = "Reasoning request timed out."):
        super().__init__(provider=provider, message=message, code="TIMEOUT", retryable=True)


class ModelUnavailableError(ProviderError):
    """Raised when the specified Bedrock model ID is unavailable or inaccessible in region."""

    def __init__(self, provider: str, message: str = "Specified model is unavailable."):
        super().__init__(provider=provider, message=message, code="MODEL_UNAVAILABLE", retryable=False)


class ReasoningProvider(ABC):
    """Abstract interface for LLM reasoning and structured engineering synthesis."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generates raw text synthesis response."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        """Generates validated Pydantic object from LLM reasoning."""
        pass
