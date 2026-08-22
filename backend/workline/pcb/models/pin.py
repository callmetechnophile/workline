"""Component pin electrical characteristics and net connection models."""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class ElectricalType(str, Enum):
    """Component pin electrical function classification."""
    POWER = "POWER"
    POWER_IN = "POWER_IN"
    POWER_OUT = "POWER_OUT"
    GROUND = "GROUND"
    INPUT = "INPUT"
    DIGITAL_IN = "DIGITAL_IN"
    OUTPUT = "OUTPUT"
    DIGITAL_OUT = "DIGITAL_OUT"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    ANALOG = "ANALOG"
    ANALOG_IN = "ANALOG_IN"
    ANALOG_OUT = "ANALOG_OUT"
    CLOCK = "CLOCK"
    RESET = "RESET"
    CONTROL = "CONTROL"
    PASSIVE = "PASSIVE"
    NO_CONNECT = "NO_CONNECT"
    NC = "NC"
    UNKNOWN = "UNKNOWN"


ElectricalPinType = ElectricalType


class Pin(BaseModel):
    """Component terminal pin record."""
    component_id: str
    pin_number: Any = 1
    name: str = ""
    pin_name: Optional[str] = None
    pin_id: Optional[str] = None
    electrical_type: ElectricalType = ElectricalType.UNKNOWN
    voltage_domain: Optional[float] = None
    current_domain: Optional[float] = None
    x: float = 0.0                     # Relative position
    y: float = 0.0
    net_id: Optional[str] = None


PCBPin = Pin
