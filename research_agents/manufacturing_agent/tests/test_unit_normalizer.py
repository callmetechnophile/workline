"""Tests for Unit Normalizer and Ambiguity Rejection (Section 32)."""
from research_agents.manufacturing_agent.services.unit_normalizer import UnitNormalizer

def test_normalize_length():
    norm = UnitNormalizer()
    val, unit = norm.normalize_length(1.0, "inch")
    assert val == 25.4
    assert unit == "mm"

    val_cm, _ = norm.normalize_length(2.5, "cm")
    assert val_cm == 25.0

    val_mil, _ = norm.normalize_length(100.0, "mil")
    assert val_mil == 2.54

def test_normalize_ambiguous_unit():
    norm = UnitNormalizer()
    val, err = norm.normalize_length(10.0, "units")
    assert val is None
    assert err == "UNIT_AMBIGUOUS"

    val_sym, err_sym = norm.normalize_length(10.0, "mils/thou")
    assert val_sym is None
    assert err_sym == "UNIT_AMBIGUOUS"

def test_normalize_surface_roughness():
    norm = UnitNormalizer()
    val, u = norm.normalize_surface_roughness(32.0, "uin")
    assert abs(val - 0.8128) < 0.001
    assert u == "um"
