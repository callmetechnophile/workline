"""Deterministic numerical quantity parser and unit normalizer for engineering data."""

import re
from typing import NamedTuple, Optional


class NormalizedQuantity(NamedTuple):
    original_value: str
    original_unit: str
    normalized_value: float
    base_unit: str


class EntityNormalizer:
    """Parses and normalizes electrical and physical quantities."""

    @classmethod
    def parse_quantity(cls, text: str) -> Optional[NormalizedQuantity]:
        clean = text.strip()

        # Voltage (e.g. 3V3, 3.3V, 500mV)
        v3_match = re.match(r"^(\d+)V(\d+)$", clean, re.IGNORECASE)
        if v3_match:
            val = float(f"{v3_match.group(1)}.{v3_match.group(2)}")
            return NormalizedQuantity(clean, "V", val, "V")

        volt_match = re.match(r"^([\d.]+)\s*(V|mV|kV)$", clean, re.IGNORECASE)
        if volt_match:
            raw_val = float(volt_match.group(1))
            unit = volt_match.group(2).upper()
            scale = 1.0
            if unit == "MV":
                scale = 0.001
            elif unit == "KV":
                scale = 1000.0
            return NormalizedQuantity(clean, volt_match.group(2), raw_val * scale, "V")

        # Current (e.g. 3A, 500mA, 20uA)
        curr_match = re.match(r"^([\d.]+)\s*(A|mA|uA|µA)$", clean, re.IGNORECASE)
        if curr_match:
            raw_val = float(curr_match.group(1))
            unit = curr_match.group(2)
            scale = 1.0
            if unit.lower() == "ma":
                scale = 0.001
            elif unit.lower() in ("ua", "µa"):
                scale = 0.000001
            return NormalizedQuantity(clean, unit, raw_val * scale, "A")

        # Resistance (e.g. 10k, 100R, 4.7M, 10kΩ)
        res_match = re.match(r"^([\d.]+)\s*(Ω|kΩ|MΩ|ohm|kohm|Mohm|R|k|M)$", clean, re.IGNORECASE)
        if res_match:
            raw_val = float(res_match.group(1))
            unit = res_match.group(2)
            scale = 1.0
            if unit.lower().startswith("k"):
                scale = 1000.0
            elif unit.lower().startswith("m") and "ohm" in unit.lower():
                scale = 1000000.0
            return NormalizedQuantity(clean, unit, raw_val * scale, "Ω")

        # Temperature (e.g. 125°C, -40C)
        temp_match = re.match(r"^([+-]?[\d.]+)\s*(°C|C|K)$", clean, re.IGNORECASE)
        if temp_match:
            raw_val = float(temp_match.group(1))
            return NormalizedQuantity(clean, "°C", raw_val, "°C")

        return None
