"""Tests for currency normalizer service."""
import pytest
from research_agents.cost_supply_chain.config import FX_UNKNOWN
from research_agents.cost_supply_chain.services.currency_normalizer import CurrencyNormalizer


def test_same_currency():
    normalizer = CurrencyNormalizer()
    val, status = normalizer.convert(100.0, "USD", "USD")
    assert val == 100.0
    assert status == "OK"


def test_eur_to_usd():
    normalizer = CurrencyNormalizer()
    # EUR rate is 1.08
    val, status = normalizer.convert(100.0, "EUR", "USD")
    assert status == "OK"
    assert val == 108.0


def test_unknown_currency():
    normalizer = CurrencyNormalizer()
    val, status = normalizer.convert(100.0, "XYZ", "USD")
    assert status == FX_UNKNOWN
    assert val == 100.0


def test_risk_buffer():
    normalizer = CurrencyNormalizer()
    buf_usd = normalizer.get_currency_risk_buffer(1000.0, "USD")
    assert buf_usd == 0.0
    buf_eur = normalizer.get_currency_risk_buffer(1000.0, "EUR", buffer_pct=5.0)
    assert buf_eur == 50.0
