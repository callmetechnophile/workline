"""Tests for Tolerance Classification and 1D Stack-Up (Section 4)."""
from research_agents.manufacturing_agent.schemas import ToleranceItem
from research_agents.manufacturing_agent.services.tolerance_engine import ToleranceEngine

def test_tolerance_classification():
    engine = ToleranceEngine()
    t_tight = engine.evaluate_tolerance({
        "component_id": "SHAFT",
        "nominal_value": 20.0,
        "unit": "mm",
        "upper_tol": 0.002,
        "lower_tol": -0.002,  # Span 0.004mm (< 0.01mm)
    })
    assert t_tight.classification == "MANUFACTURING_CONCERN"

def test_1d_stackup_calculation():
    engine = ToleranceEngine()
    items = [
        ToleranceItem(component_id="C1", feature_name="F1", nominal_value=10.0, unit="mm", upper_tol=0.1, lower_tol=-0.1),
        ToleranceItem(component_id="C2", feature_name="F2", nominal_value=20.0, unit="mm", upper_tol=0.2, lower_tol=-0.2),
    ]
    res = engine.calculate_1d_stackup(items)
    assert res["status"] == "SUCCESS"
    assert res["total_nominal_mm"] == 30.0
    assert res["worst_case_upper_mm"] == 0.3
    assert res["worst_case_lower_mm"] == -0.3
