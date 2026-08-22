"""PCB Power Architecture and Conductor Integrity models."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PowerRail(BaseModel):
    """Regulated voltage domain rail."""
    name: str                          # e.g., "3V3", "5V", "12V", "V_BATT"
    voltage: float                     # Volts (e.g., 3.3)
    max_current: float                 # Amperes (e.g., 1.5)
    estimated_current: float           # Amperes (e.g., 0.65)
    regulator: Optional[str] = None    # e.g., "U2 (TPS62130)"
    source: Optional[str] = None       # e.g., "Battery / Buck Converter"
    consumers: List[str] = Field(default_factory=list) # e.g. ["U1 (ESP32)", "U3 (BME280)"]


class PowerViolationFlag(BaseModel):
    """Specific power integrity warning or violation."""
    rail_name: str
    severity: str                      # WARN, FAIL
    description: str
    recommendation: str


class PowerModel(BaseModel):
    """Integrates with the existing Power Agent."""
    rails: Dict[str, PowerRail] = Field(default_factory=dict)
    total_power_watts: float = 0.0
    flags: List[PowerViolationFlag] = Field(default_factory=list)
    has_overloaded_rail: bool = False
    has_missing_return_path: bool = False
    missing_decoupling_capacitors: List[str] = Field(default_factory=list)
