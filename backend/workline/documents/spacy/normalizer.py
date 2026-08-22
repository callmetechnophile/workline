"""Engineering unit and value normalizer."""

import re
from typing import Tuple


class EntityNormalizer:
    """Normalizes voltages, currents, temperatures, and tolerances consistently."""

    @classmethod
    def normalize_voltage(cls, text: str) -> Tuple[str, str]:
        clean = text.strip()
        # 3V3 -> 3.3 V
        v_match = re.match(r"^(\d+)V(\d+)$", clean, re.IGNORECASE)
        if v_match:
            return f"{v_match.group(1)}.{v_match.group(2)} V", "V"

        std_match = re.match(r"^([\d.]+)\s*(V|mV|kV)$", clean, re.IGNORECASE)
        if std_match:
            val, unit = std_match.group(1), std_match.group(2).upper()
            return f"{val} {unit}", unit

        return clean, "V"

    @classmethod
    def normalize_current(cls, text: str) -> Tuple[str, str]:
        clean = text.strip()
        match = re.match(r"^([\d.]+)\s*(A|mA|uA|µA)$", clean, re.IGNORECASE)
        if match:
            val, unit = match.group(1), match.group(2)
            return f"{val} {unit}", unit
        return clean, "A"

    @classmethod
    def normalize_temperature(cls, text: str) -> Tuple[str, str]:
        clean = text.strip()
        match = re.match(r"^([+-]?[\d.]+)\s*(°C|C|K|°F|F)$", clean, re.IGNORECASE)
        if match:
            return f"{match.group(1)} °C", "°C"
        return clean, "°C"
