"""
Unit tests for UnitEngine and dimensional consistency checking (Sections 16–18, 97).
"""

import pytest
from research_agents.engineering_simulation.services.unit_system import UnitEngine


def test_unit_engine_and_dimensional_checking():
    unit_engine = UnitEngine()

    # 1. Valid Conversion: P = 3.3V * 150mA = 0.495W
    p = unit_engine.calculate_power_watts(3.3, "V", 150.0, "mA")
    assert p == 0.495

    # 2. Thermal Rise: Ambient 25°C + (0.495W * 45°C/W) = 47.27°C
    t = unit_engine.calculate_temperature_rise(p, 45.0, 25.0)
    assert t == 47.27

    # 3. Dimensional Mismatch -> MODEL_ERROR (Section 97)
    with pytest.raises(ValueError, match="MODEL_ERROR"):
        unit_engine.calculate_power_watts(3.3, "kg", 150.0, "mA")
