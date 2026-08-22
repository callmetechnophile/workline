"""Safe dimensional and unit conversion engine for engineering validation."""

import re
from typing import NamedTuple, Optional, Tuple


class ConversionResult(NamedTuple):
    success: bool = True
    converted_value: float = 0.0
    error: Optional[str] = None


UNIT_TABLE = {
    # Voltage (Base: V)
    "V": ("VOLTAGE", 1.0),
    "MV": ("VOLTAGE", 0.001),
    "KV": ("VOLTAGE", 1000.0),
    # Current (Base: A)
    "A": ("CURRENT", 1.0),
    "MA": ("CURRENT", 0.001),
    "UA": ("CURRENT", 0.000001),
    "µA": ("CURRENT", 0.000001),
    # Power (Base: W)
    "W": ("POWER", 1.0),
    "MW": ("POWER", 0.001),
    "KW": ("POWER", 1000.0),
    # Resistance (Base: Ω)
    "Ω": ("RESISTANCE", 1.0),
    "OHM": ("RESISTANCE", 1.0),
    "KΩ": ("RESISTANCE", 1000.0),
    "KOHM": ("RESISTANCE", 1000.0),
    "MΩ": ("RESISTANCE", 1000000.0),
    "MOHM": ("RESISTANCE", 1000000.0),
    # Frequency (Base: Hz)
    "HZ": ("FREQUENCY", 1.0),
    "KHZ": ("FREQUENCY", 1000.0),
    "MHZ": ("FREQUENCY", 1000000.0),
    "GHZ": ("FREQUENCY", 1000000000.0),
    # Temperature (Base: °C)
    "°C": ("TEMPERATURE", 1.0),
    "C": ("TEMPERATURE", 1.0),
}


class UnitValidator:
    """Validates and converts engineering units safely."""

    @classmethod
    def get_dimension(cls, unit_str: str) -> Optional[str]:
        entry = UNIT_TABLE.get(unit_str.upper()) or UNIT_TABLE.get(unit_str)
        return entry[0] if entry else None

    @classmethod
    def convert(cls, value: float, from_unit_str: str, to_unit_str: str) -> Tuple[bool, float, Optional[str]]:
        from_entry = UNIT_TABLE.get(from_unit_str.upper()) or UNIT_TABLE.get(from_unit_str)
        to_entry = UNIT_TABLE.get(to_unit_str.upper()) or UNIT_TABLE.get(to_unit_str)

        if not from_entry or not to_entry:
            return False, 0.0, f"Unrecognized unit '{from_unit_str}' or '{to_unit_str}'"

        if from_entry[0] != to_entry[0]:
            return False, 0.0, f"Incompatible dimensions: Cannot convert {from_entry[0]} ('{from_unit_str}') to {to_entry[0]} ('{to_unit_str}')"

        base_val = value * from_entry[1]
        target_val = base_val / to_entry[1]
        return True, target_val, None
