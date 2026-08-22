"""Component pin electrical characteristics and net connection models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ElectricalType(str, Enum):
    """Component pin electrical function classification."""
    POWER = "POWER"
    GROUND = "GROUND"
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    ANALOG = "ANALOG"
    CLOCK = "CLOCK"
    PASSIVE = "PASSIVE"
    NO_CONNECT = "NO_CONNECT"
    UNKNOWN = "UNKNOWN"


class Pin(BaseModel):
    """Component terminal pin record."""
    component_id: str
    pin_number: int
    name: str
    electrical_type: ElectricalType = ElectricalType.UNKNOWN
    x: float = 0.0                     # Relative position
    y: float = 0.0
    net_id: Optional[str] = None
