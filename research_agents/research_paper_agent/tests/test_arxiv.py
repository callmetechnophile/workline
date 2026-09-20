"""
Unit tests for ArxivProvider adapter and Atom XML parsing.
"""

import pytest
import httpx
from research_agents.research_paper_agent.providers.base import (
    MalformedResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from research_agents.research_paper_agent.providers.arxiv import ArxivProvider

SAMPLE_ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <link href="http://arxiv.org/api/query?search_query=all:slam&amp;id_list=&amp;start=0&amp;max_results=1" rel="self" type="application/atom+xml"/>
  <title type="html">ArXiv Query: search_query=all:slam</title>
  <id>http://arxiv.org/api/12345</id>
  <updated>2026-09-20T00:00:00-04:00</updated>
  <entry>
    <id>http://arxiv.org/abs/2403.12345v1</id>
    <updated>2024-03-15T18:22:10Z</updated>
    <published>2024-03-15T18:22:10Z</published>
    <title> Real-Time Visual SLAM for Autonomous Aerial Vehicles </title>
    <summary> We propose a high-performance visual SLAM pipeline running on edge compute. </summary>
    <author>
      <name>Alice Smith</name>
    </author>
    <author>
      <name>Bob Jones</name>
    </author>
    <arxiv:doi>10.1109/ROBOTICS.2024.999</arxiv:doi>
    <link href="http://arxiv.org/abs/2403.12345v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/2403.12345v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category term="cs.RO" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.RO" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.CV" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
"""


@pytest.mark.asyncio
async def test_arxiv_successful_search():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, text=SAMPLE_ARXIV_XML)
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = ArxivProvider(http_client=client)
        records = await provider.search("visual SLAM", limit=5)

    assert len(records) == 1
    rec = records[0]
    assert rec.paper_id == "2403.12345v1"
    assert rec.title == "Real-Time Visual SLAM for Autonomous Aerial Vehicles"
    assert rec.authors == ["Alice Smith", "Bob Jones"]
    assert rec.doi == "10.1109/ROBOTICS.2024.999"
    assert rec.venue == "arXiv"
    assert rec.paper_url == "http://arxiv.org/abs/2403.12345v1"
    assert rec.pdf_url == "http://arxiv.org/pdf/2403.12345v1"
    assert "cs.RO" in rec.keywords
    assert "cs.CV" in rec.keywords
    assert rec.raw_metadata.get("source") == "arxiv"


@pytest.mark.asyncio
async def test_arxiv_empty_query():
    provider = ArxivProvider()
    records = await provider.search("   ")
    assert records == []


@pytest.mark.asyncio
async def test_arxiv_rate_limit_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(429, text="Rate limit exceeded")
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = ArxivProvider(http_client=client)
        with pytest.raises(ProviderRateLimitError):
            await provider.search("slam")


@pytest.mark.asyncio
async def test_arxiv_server_error():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(503, text="Service Unavailable")
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = ArxivProvider(http_client=client)
        with pytest.raises(ProviderUnavailableError):
            await provider.search("slam")


@pytest.mark.asyncio
async def test_arxiv_timeout():
    def raise_timeout(req):
        raise httpx.ReadTimeout("Connection timed out")

    mock_transport = httpx.MockTransport(raise_timeout)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = ArxivProvider(http_client=client)
        with pytest.raises(ProviderTimeoutError):
            await provider.search("slam")


@pytest.mark.asyncio
async def test_arxiv_malformed_xml():
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, text="<not valid xml")
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        provider = ArxivProvider(http_client=client)
        with pytest.raises(MalformedResponseError):
            await provider.search("slam")
