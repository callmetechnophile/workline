"""Tests for operational unit normalizer."""
from research_agents.deployment_operations.services.unit_normalizer import OperationalUnitNormalizer


def test_time_normalization():
    norm = OperationalUnitNormalizer()
    assert norm.normalize_time_seconds(2.0, "min") == 120.0
    assert norm.normalize_time_seconds(1.0, "hr") == 3600.0
    assert norm.normalize_time_seconds(45.0, "s") == 45.0


def test_memory_normalization():
    norm = OperationalUnitNormalizer()
    assert norm.normalize_memory_mb(4.0, "GB") == 4096.0
    assert norm.normalize_memory_mb(512.0, "MB") == 512.0


def test_voltage_normalization():
    norm = OperationalUnitNormalizer()
    assert norm.normalize_voltage_v(12.0, "V") == 12.0
    assert norm.normalize_voltage_v(5000.0, "mV") == 5.0
    assert norm.normalize_voltage_v(1.2, "kV") == 1200.0
