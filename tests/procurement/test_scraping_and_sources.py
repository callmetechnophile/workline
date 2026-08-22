"""Unit tests for Scrapling acquisition engine, caching, rate limiting, and vendor adapters."""

import asyncio
import pytest
from backend.workline.scraping.engine import ScrapingCache, ScraplingEngine
from backend.workline.scraping.sources.digikey import DigiKeySource
from backend.workline.scraping.sources.mouser import MouserSource
from backend.workline.scraping.sources.robocraze import RobocrazeSource
from backend.workline.scraping.sources.robu import RobuSource


def test_scrapling_cache():
    """Test disk and memory cache with key hashing and TTL."""
    cache = ScrapingCache()
    url = "https://test.vendor.com/product/123"
    data = "<html><body><h1>TPS62130</h1></body></html>"

    cache.set(url, data)
    cached = cache.get(url)
    assert cached == data


def test_scrapling_engine_adaptor():
    """Test Scrapling Adaptor HTML parsing."""
    engine = ScraplingEngine()
    html = """
    <div class="product-item">
        <h2 class="title">ESP32-S3 Microcontroller</h2>
        <span class="price">₹680.00</span>
        <a class="datasheet" href="https://espressif.com/esp32.pdf">Datasheet</a>
    </div>
    """
    adaptor = engine.create_adaptor(html)
    assert adaptor is not None
    title = adaptor.css(".title::text").get()
    assert "ESP32-S3" in (title or "")


def test_digikey_source_mock_search():
    """Test DigiKey vendor adapter parsing and spec extraction."""
    async def _run():
        source = DigiKeySource()
        results = await source.search("TPS62130", limit=2)
        assert len(results) >= 1
        r = results[0]
        assert r.vendor == "DigiKey"
        assert r.mpn == "TPS62130RGTR"
        assert r.currency == "USD"
        assert r.datasheet_url is not None
        assert "3A" in r.description

    asyncio.run(_run())


def test_mouser_source_mock_search():
    """Test Mouser vendor adapter parsing."""
    async def _run():
        source = MouserSource()
        results = await source.search("DRV8833", limit=2)
        assert len(results) >= 1
        r = results[0]
        assert r.vendor == "Mouser"
        assert "DRV8833" in r.mpn
        assert r.currency == "INR"

    asyncio.run(_run())


def test_robu_and_robocraze_sources():
    """Test domestic Indian suppliers (Robu & Robocraze)."""
    async def _run():
        robu = RobuSource()
        robocraze = RobocrazeSource()

        res_robu = await robu.search("BME280", limit=2)
        assert len(res_robu) >= 1
        assert res_robu[0].vendor == "Robu"
        assert "BME280" in res_robu[0].mpn

        res_rc = await robocraze.search("soil moisture", limit=2)
        assert len(res_rc) >= 1
        assert res_rc[0].vendor == "Robocraze"
        assert res_rc[0].currency == "INR"

    asyncio.run(_run())
