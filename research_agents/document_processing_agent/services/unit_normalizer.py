"""
Engineering physical and electrical unit detector and normalizer.
Converts values to standard SI base units (mA -> A, kHz/MHz/GHz -> Hz, etc.)
while preserving original strings.
"""

import re
from typing import Optional, Tuple


class UnitNormalizer:
    """Normalizes electrical, frequency, power, and physical units to SI standards."""

    UNIT_CONVERSIONS = {
        # Voltage
        "mv": (1e-3, "V"),
        "v": (1.0, "V"),
        "kv": (1e3, "V"),
        # Current
        "ua": (1e-6, "A"),
        "µa": (1e-6, "A"),
        "ma": (1e-3, "A"),
        "a": (1.0, "A"),
        # Power
        "mw": (1e-3, "W"),
        "w": (1.0, "W"),
        "kw": (1e3, "W"),
        # Frequency
        "hz": (1.0, "Hz"),
        "khz": (1e3, "Hz"),
        "mhz": (1e6, "Hz"),
        "ghz": (1e9, "Hz"),
        # Resistance
        "mohm": (1e-3, "Ω"),
        "mω": (1e-3, "Ω"),
        "ohm": (1.0, "Ω"),
        "ω": (1.0, "Ω"),
        "kohm": (1e3, "Ω"),
        "kω": (1e3, "Ω"),
        "mohm_mega": (1e6, "Ω"),
        # Memory
        "kb": (1e3, "Bytes"),
        "mb": (1e6, "Bytes"),
        "gb": (1e9, "Bytes"),
    }

    UNIT_REGEX = re.compile(
        r"([-+]?\d+(\.\d+)?)\s*(kV|mV|V|µA|uA|mA|A|kW|mW|W|GHz|MHz|kHz|Hz|kΩ|kohm|MΩ|mohm|Ω|ohm|GB|MB|KB|°C|degC)\b",
        re.IGNORECASE,
    )

    def normalize(self, raw_expression: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Extracts value and converts to standard SI base unit.

        Returns:
            (normalized_value, normalized_unit)
        """
        match = self.UNIT_REGEX.search(raw_expression.strip())
        if not match:
            return None, None

        val_str = match.group(1)
        unit_str = match.group(3).lower()

        try:
            val_float = float(val_str)
        except ValueError:
            return None, None

        if unit_str in self.UNIT_CONVERSIONS:
            multiplier, base_unit = self.UNIT_CONVERSIONS[unit_str]
            normalized_val = round(val_float * multiplier, 6)
            return normalized_val, base_unit

        if "°c" in unit_str or "degc" in unit_str:
            return val_float, "°C"

        return val_float, match.group(3)
