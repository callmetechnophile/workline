"""
Reasoning provider interfaces and exceptions for EngineeringArchitectureAgent.
Re-exports from deep_research_agent.providers.base for unified infrastructure.
"""

from research_agents.deep_research_agent.providers.base import (
    ModelUnavailableError,
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ReasoningProvider,
)

__all__ = [
    "ReasoningProvider",
    "ProviderError",
    "ProviderAuthenticationError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    "ModelUnavailableError",
]
