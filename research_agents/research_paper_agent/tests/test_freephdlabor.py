"""
Unit tests for Freephdlabor provider adapter and error translation.
"""

import pytest
import httpx
from research_agents.research_paper_agent.providers.base import (
    MalformedResponseError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from research_agents.research_paper_agent.providers.freephdlabor import FreephdlaborProvider


@pytest.mark.asyncio
async def test_freephdlabor_successful_search():
    sample_response = {
        "papers": [
            {
                "id": "paper_101",
                "title": "Real-Time Thermal Vision for Autonomous UAV Search",
                "authors": ["Alice Smith", "Bob Jones"],
                "abstract": "We present a thermal imaging framework on edge Jetson devices.",
                "publication_date": "2024-05-12",
                "doi": "10.1109/UAV.2024.101",
                "venue": "IEEE Robotics and Automation Letters",
                "paper_url": "https://ieeexplore.ieee.org/document/101",
                "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=101.pdf",
                "citation_count": 14,
                "keywords": ["UAV", "thermal imaging", "edge compute"],
            }
        ]
    }

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=sample_response)
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = FreephdlaborProvider(http_client=client)
        records = await provider.search("thermal UAV search", limit=5)

    assert len(records) == 1
    rec = records[0]
    assert rec.paper_id == "paper_101"
    assert rec.title == "Real-Time Thermal Vision for Autonomous UAV Search"
    assert len(rec.authors) == 2
    assert rec.doi == "10.1109/UAV.2024.101"
    assert rec.citation_count == 14


@pytest.mark.asyncio
async def test_freephdlabor_auth_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(401, json={"error": "Invalid API key"})
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = FreephdlaborProvider(http_client=client)
        with pytest.raises(ProviderAuthenticationError):
            await provider.search("thermal vision")


@pytest.mark.asyncio
async def test_freephdlabor_rate_limit_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(429, json={"error": "Too Many Requests"})
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = FreephdlaborProvider(http_client=client)
        with pytest.raises(ProviderRateLimitError) as exc_info:
            await provider.search("thermal vision")
        assert exc_info.value.retryable is True


@pytest.mark.asyncio
async def test_freephdlabor_timeout_error():
    def raise_timeout(req):
        raise httpx.TimeoutException("Connection timed out")

    mock_transport = httpx.MockTransport(raise_timeout)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = FreephdlaborProvider(http_client=client)
        with pytest.raises(ProviderTimeoutError) as exc_info:
            await provider.search("thermal vision")
        assert exc_info.value.retryable is True


@pytest.mark.asyncio
async def test_freephdlabor_server_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(503, text="Service Unavailable")
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = FreephdlaborProvider(http_client=client)
        with pytest.raises(ProviderUnavailableError):
            await provider.search("thermal vision")


@pytest.mark.asyncio
async def test_freephdlabor_empty_query():
    provider = FreephdlaborProvider()
    records = await provider.search("   ")
    assert records == []


@pytest.mark.asyncio
async def test_freephdlabor_missing_metadata_preservation():
    # Sparse payload
    sample_response = [
        {
            "name": "Minimal Paper Title Without Extras",
        }
    ]

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=sample_response)
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = FreephdlaborProvider(http_client=client)
        records = await provider.search("minimal title")

    assert len(records) == 1
    rec = records[0]
    assert rec.title == "Minimal Paper Title Without Extras"
    assert rec.abstract is None
    assert rec.doi is None
    assert rec.pdf_url is None
    assert rec.citation_count is None
    assert rec.authors == []
