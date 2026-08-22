"""Signal Integrity (SI) and Power Integrity (PI) structured feature models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SignalIntegrityFeature(BaseModel):
    """Structured high-speed signal integrity engineering features."""
    net_id: str
    signal_frequency: float = 0.0      # Hz (e.g. 100MHz SPI, 400kHz I2C)
    rise_time_ns: float = 2.0          # ns
    fall_time_ns: float = 2.0          # ns
    trace_length_mm: float = 25.0      # mm
    trace_width_mm: float = 0.254      # mm
    trace_thickness_mm: float = 0.035  # mm
    dielectric_height_mm: float = 0.20 # mm
    dielectric_constant: float = 4.4
    target_impedance_ohms: float = 50.0 # ohms (single-ended) or 90/100 (differential)
    is_differential: bool = False
    estimated_impedance_ohms: Optional[float] = None
    estimated_propagation_delay_ps: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)


class PowerIntegrityFeature(BaseModel):
    """Structured power delivery network (PDN) impedance and decoupling features."""
    rail_name: str
    rail_voltage: float = 3.3
    load_current_amps: float = 0.5
    ripple_frequency_hz: float = 500000.0 # 500 kHz buck ripple
    decoupling_capacitance_uf: float = 10.0 # uF
    equivalent_series_resistance_mohm: float = 15.0 # mOhm
    trace_resistance_mohm: float = 25.0
    trace_inductance_nh: float = 4.5
    estimated_pdn_impedance_mohm: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)


class SignalIntegrityModel(BaseModel):
    """Signal and Power Integrity feature collections."""
    si_features: List[SignalIntegrityFeature] = Field(default_factory=list)
    pi_features: List[PowerIntegrityFeature] = Field(default_factory=list)
