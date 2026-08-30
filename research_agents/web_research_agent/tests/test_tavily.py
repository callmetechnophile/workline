"""
Unit tests for Tavily provider adapter and error translation.
"""

import pytest
import httpx
from research_agents.web_research_agent.providers.base import (
    InvalidURLError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from research_agents.web_research_agent.providers.tavily import TavilyProvider


@pytest.mark.asyncio
async def test_tavily_search_success():
    sample_response = {
        "results": [
            {
                "title": "Jetson Orin Nano Developer Kit Documentation",
                "url": "https://developer.nvidia.com/embedded/jetson-orin-nano-developer-kit",
                "content": "NVIDIA Jetson Orin Nano modules deliver up to 40 TOPS of AI performance in the smallest form factor.",
                "snippet": "40 TOPS AI performance with 6-core ARM CPU and Ampere GPU.",
                "published_date": "2023-09-10",
                "publisher": "NVIDIA Corporation",
            }
        ]
    }

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=sample_response)
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = TavilyProvider(http_client=client)
        results = await provider.search("Jetson Orin Nano documentation", limit=5)

    assert len(results) == 1
    res = results[0]
    assert res.title == "Jetson Orin Nano Developer Kit Documentation"
    assert res.url == "https://developer.nvidia.com/embedded/jetson-orin-nano-developer-kit"
    assert res.source_tool == "tavily"
    assert "40 TOPS" in (res.content or "")


@pytest.mark.asyncio
async def test_tavily_auth_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(401, json={"error": "Unauthorized API key"})
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = TavilyProvider(http_client=client)
        with pytest.raises(ProviderAuthenticationError):
            await provider.search("ESP32-S3 pinout")


@pytest.mark.asyncio
async def test_tavily_rate_limit_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(429, json={"error": "Rate limit exceeded"})
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = TavilyProvider(http_client=client)
        with pytest.raises(ProviderRateLimitError) as exc:
            await provider.search("ESP32-S3 pinout")
        assert exc.value.retryable is True


@pytest.mark.asyncio
async def test_tavily_timeout():
    def raise_timeout(req):
        raise httpx.TimeoutException("Search timed out")

    mock_transport = httpx.MockTransport(raise_timeout)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = TavilyProvider(http_client=client)
        with pytest.raises(ProviderTimeoutError):
            await provider.search("thermal camera UAV")


@pytest.mark.asyncio
async def test_tavily_extract_invalid_url():
    provider = TavilyProvider()
    with pytest.raises(InvalidURLError):
        await provider.extract("invalid-url-without-scheme")
