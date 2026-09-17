"""Tests for Statistical Process Capability (Cp/Cpk) and Rejection of Fabricated Data (Section 9)."""
from research_agents.manufacturing_agent.services.variation_engine import VariationEngine

def test_insufficient_sample_data():
    engine = VariationEngine()
    # 5 samples (< 30) must return DATA_INSUFFICIENT
    res = engine.evaluate_capability("Hole Diameter", samples=[10.0, 10.01, 9.99, 10.02, 9.98], usl=10.05, lsl=9.95)
    assert res.status == "DATA_INSUFFICIENT"
    assert res.is_sufficient is False
    assert res.cp is None

def test_sufficient_sample_data():
    engine = VariationEngine()
    # 30 valid samples with mean 10.0 and known variance
    samples = [10.0 + (0.01 if i % 2 == 0 else -0.01) for i in range(30)]
    res = engine.evaluate_capability("Width", samples=samples, usl=10.1, lsl=9.9)
    assert res.status == "DATA_SUFFICIENT"
    assert res.is_sufficient is True
    assert res.cp is not None
    assert res.cpk is not None
    assert res.cp > 1.0
