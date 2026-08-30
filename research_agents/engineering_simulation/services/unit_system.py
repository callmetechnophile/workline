"""
Deterministic physical unit handling and dimensional consistency checking (Sections 16–18, 97).
"""

from typing import Any, Dict


class UnitEngine:
    """Validates physical dimensions and converts units deterministically."""

    def validate_power_dimensions(self, voltage_unit: str, current_unit: str) -> bool:
        v_valid = voltage_unit.lower() in ("v", "volt", "volts", "mv")
        i_valid = current_unit.lower() in ("a", "amp", "amps", "ma")
        return v_valid and i_valid

    def calculate_power_watts(
        self,
        voltage: float,
        voltage_unit: str,
        current: float,
        current_unit: str,
    ) -> float:
        if not self.validate_power_dimensions(voltage_unit, current_unit):
            raise ValueError("MODEL_ERROR: Incompatible electrical units for power calculation.")

        # Convert to Base SI: Volts and Amps
        v_si = voltage * 1e-3 if voltage_unit.lower() == "mv" else voltage
        i_si = current * 1e-3 if current_unit.lower() == "ma" else current

        return round(v_si * i_si, 4)

    def calculate_temperature_rise(
        self,
        power_watts: float,
        thermal_resistance_c_per_w: float,
        ambient_temp_c: float = 25.0,
    ) -> float:
        delta_t = power_watts * thermal_resistance_c_per_w
        return round(ambient_temp_c + delta_t, 2)
