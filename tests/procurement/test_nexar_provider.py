"""Unit and integration tests for official Nexar API Provider and Client."""

import asyncio
import pytest
from backend.workline.procurement.models import (
    CheckStatus,
    ComponentRequirement,
    FreshnessStatus,
)
from backend.workline.procurement.providers.nexar import NexarClient, NexarProvider


def test_nexar_client_configuration():
    """Test NexarClient initialization and credential detection."""
    client = NexarClient(client_id="test_id", client_secret="test_sec")
    assert client.has_credentials is True
    assert "graphql" in client.endpoint


def test_nexar_provider_mpn_search():
    """Test exact MPN search via Nexar provider (TPS62130)."""
    async def _run():
        provider = NexarProvider()
        cand = await provider.search_mpn("TPS62130RGTR")
        assert cand is not None
        assert cand.manufacturer == "Texas Instruments"
        assert cand.manufacturer_part_number == "TPS62130RGTR"
        assert cand.component_id == "component:texas_instruments_tps62130rgtr"
        assert cand.electrical.nominal_voltage == 3.3
        assert cand.electrical.current_max == 3.0
        assert cand.pricing.unit_price is not None
        assert len(cand.listings) >= 1
        assert cand.datasheet is not None
        assert "ti.com" in cand.datasheet.url

    asyncio.run(_run())


def test_nexar_provider_structured_search():
    """Test category/descriptive search via Nexar provider."""
    async def _run():
        provider = NexarProvider()
        candidates = await provider.search_components("ESP32-S3 microcontroller", limit=2)
        assert len(candidates) >= 1
        cand = candidates[0]
        assert "ESP32-S3" in cand.manufacturer_part_number
        assert cand.interfaces.i2c is True
        assert cand.interfaces.spi is True
        assert cand.interfaces.uart is True
        assert cand.availability.stock is not None
        assert cand.availability.stock > 0

    asyncio.run(_run())


def test_nexar_offers_mapping():
    """Test mapping of distributor offers to canonical VendorListing models."""
    async def _run():
        provider = NexarProvider()
        offers = await provider.get_offers("TPS62130RGTR")
        assert len(offers) >= 1
        offer = offers[0]
        assert offer.currency == "INR"
        assert offer.unit_price is not None
        assert offer.unit_price > 0.0
        assert offer.freshness == FreshnessStatus.FRESH
        assert offer.source == "Nexar"

    asyncio.run(_run())


def test_nexar_datasheet_discovery():
    """Test discovery of verified technical documentation."""
    async def _run():
        provider = NexarProvider()
        datasheets = await provider.get_datasheets("BME280")
        assert len(datasheets) >= 1
        ds = datasheets[0]
        assert ds.manufacturer == "Bosch Sensortec"
        assert ds.mpn == "BME280"
        assert "bosch-sensortec.com" in ds.url

    asyncio.run(_run())
