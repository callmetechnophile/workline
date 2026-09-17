"""
Robust engineering unit normalization and ambiguity detection service (Section 32).
"""

from typing import Optional, Tuple
from research_agents.manufacturing_agent.config import manufacturing_config


class UnitNormalizer:
    """Normalizes engineering dimensions, force, torque, pressure, and surface roughness to SI/standard units."""

    def __init__(self):
        self.config = manufacturing_config.units

    def normalize_length(self, value: float, unit: str) -> Tuple[Optional[float], str]:
        """Convert any supported length unit to mm. Returns (normalized_mm, 'mm') or (None, 'UNIT_AMBIGUOUS')."""
        if not unit or not isinstance(unit, str):
            return None, "UNIT_AMBIGUOUS"

        clean_unit = unit.strip().lower()
        factor = self.config.length_to_mm.get(clean_unit)
        if factor is not None:
            return round(value * factor, 6), "mm"

        # Explicit check for ambiguous symbols like quotes (", ') or unknown tokens
        if clean_unit in ('"', "''", "mils/thou", "pts", "units"):
            return None, "UNIT_AMBIGUOUS"

        return None, "UNIT_AMBIGUOUS"

    def normalize_force(self, value: float, unit: str) -> Tuple[Optional[float], str]:
        """Convert force to Newtons (N)."""
        if not unit:
            return None, "UNIT_AMBIGUOUS"
        clean = unit.strip().lower()
        factor = self.config.force_to_newton.get(clean)
        if factor is not None:
            return round(value * factor, 6), "N"
        return None, "UNIT_AMBIGUOUS"

    def normalize_torque(self, value: float, unit: str) -> Tuple[Optional[float], str]:
        """Convert torque to Newton-meters (N*m)."""
        if not unit:
            return None, "UNIT_AMBIGUOUS"
        clean = unit.strip().lower()
        factor = self.config.torque_to_nm.get(clean)
        if factor is not None:
            return round(value * factor, 6), "N*m"
        return None, "UNIT_AMBIGUOUS"

    def normalize_surface_roughness(self, value: float, unit: str) -> Tuple[Optional[float], str]:
        """Convert surface roughness Ra to micrometers (um)."""
        if not unit:
            return None, "UNIT_AMBIGUOUS"
        clean = unit.strip().lower()
        if clean in ("um", "µm", "micron", "microns", "micrometer"):
            return round(value, 4), "um"
        elif clean in ("uin", "microinch", "micro-inch", "µin"):
            # 1 microinch = 0.0254 um
            return round(value * 0.0254, 4), "um"
        return None, "UNIT_AMBIGUOUS"
