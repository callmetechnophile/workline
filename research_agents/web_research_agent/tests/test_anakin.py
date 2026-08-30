"""
Unit tests for Anakin provider adapter (scraping, crawling, JS rendering, errors).
"""

import pytest
import httpx
from research_agents.web_research_agent.providers.anakin import AnakinProvider
from research_agents.web_research_agent.providers.base import (
    ExtractionError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)


@pytest.mark.asyncio
async def test_anakin_scrape_success():
    sample_response = {
        "title": "ESP32-S3 Series Datasheet — Espressif",
        "markdown": "## Specifications\nOperating voltage: 3.0V to 3.6V. Dual-core Xtensa LX7 MCU up to 240MHz. Supports 2.4 GHz Wi-Fi and Bluetooth 5 (LE).",
        "description": "Official electrical and pinout specifications for ESP32-S3.",
        "site_name": "Espressif Systems",
    }

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=sample_response)
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = AnakinProvider(http_client=client)
        result = await provider.extract("https://espressif.com/en/products/socs/esp32-s3")

    assert result is not None
    assert result.title == "ESP32-S3 Series Datasheet — Espressif"
    assert result.source_tool == "anakin"
    assert "Xtensa LX7" in (result.content or "")


@pytest.mark.asyncio
async def test_anakin_crawl_success():
    sample_response = {
        "pages": [
            {
                "url": "https://docs.ros.org/en/humble/index.html",
                "title": "ROS 2 Humble Documentation",
                "text": "ROS 2 is a set of software libraries and tools for building robot applications.",
            },
            {
                "url": "https://docs.ros.org/en/humble/Installation.html",
                "title": "ROS 2 Humble Installation",
                "text": "Instructions for installing ROS 2 on Ubuntu Linux.",
            },
        ]
    }

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=sample_response)
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = AnakinProvider(http_client=client)
        results = await provider.crawl("https://docs.ros.org/en/humble/")

    assert len(results) == 2
    assert results[0].url == "https://docs.ros.org/en/humble/index.html"
    assert results[1].title == "ROS 2 Humble Installation"


@pytest.mark.asyncio
async def test_anakin_auth_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(401, json={"error": "Invalid API key"})
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = AnakinProvider(http_client=client)
        with pytest.raises(ProviderAuthenticationError):
            await provider.extract("https://example.com/component")


@pytest.mark.asyncio
async def test_anakin_rate_limit_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(429, json={"error": "Rate limit exceeded"})
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = AnakinProvider(http_client=client)
        with pytest.raises(ProviderRateLimitError):
            await provider.extract("https://example.com/component")
