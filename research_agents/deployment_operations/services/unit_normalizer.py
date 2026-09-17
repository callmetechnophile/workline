"""
Operational unit normalization and validation service.
"""

from typing import Any, Dict, Optional, Tuple


class OperationalUnitNormalizer:
    """Preserves original units while providing normalized values for comparison."""

    def normalize_time_seconds(self, value: float, unit: str) -> float:
        u = unit.lower().strip()
        if u in ["s", "sec", "second", "seconds"]:
            return value
        elif u in ["min", "minute", "minutes"]:
            return value * 60.0
        elif u in ["h", "hr", "hour", "hours"]:
            return value * 3600.0
        elif u in ["d", "day", "days"]:
            return value * 86400.0
        return value

    def normalize_memory_mb(self, value: float, unit: str) -> float:
        u = unit.lower().strip()
        if u in ["mb", "mbyte", "megabyte"]:
            return value
        elif u in ["gb", "gbyte", "gigabyte"]:
            return value * 1024.0
        elif u in ["tb", "tbyte", "terabyte"]:
            return value * 1024.0 * 1024.0
        elif u in ["kb", "kbyte"]:
            return value / 1024.0
        return value

    def normalize_voltage_v(self, value: float, unit: str) -> float:
        u = unit.lower().strip()
        if u in ["v", "volt", "volts"]:
            return value
        elif u in ["mv", "millivolt", "millivolts"]:
            return value / 1000.0
        elif u in ["kv", "kilovolt", "kilovolts"]:
            return value * 1000.0
        return value
