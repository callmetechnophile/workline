"""PCB Net and Netlist topology models."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class NetClass(str, Enum):
    """Net classification for design rules and impedance constraints."""
    POWER = "POWER"
    GROUND = "GROUND"
    ANALOG = "ANALOG"
    DIGITAL = "DIGITAL"
    HIGH_SPEED = "HIGH_SPEED"
    CLOCK = "CLOCK"
    DIFFERENTIAL = "DIFFERENTIAL"


class NetNode(BaseModel):
    """Pin endpoint attached to a Net."""
    component_id: str                  # PCBComponent id or reference designator
    pin_number: int
    pin_name: Optional[str] = None


class Net(BaseModel):
    """Electrical Net interconnecting component pins across the board."""
    id: str                            # e.g. "net_gnd", "net_3v3", "net_sda"
    name: str                          # e.g. "GND", "VCC_3V3", "I2C_SDA", "UART_TX"
    net_class: NetClass = NetClass.DIGITAL
    priority: int = 1                  # 1 to 5 (5 highest)
    signal_type: str = "LOGIC"

    voltage: float = 3.3               # Nominal volts
    current: float = 0.05              # Max estimated amps
    frequency: float = 0.0             # Operating frequency (Hz)
    criticality: str = "MEDIUM"        # LOW, MEDIUM, HIGH, CRITICAL

    nodes: List[NetNode] = Field(default_factory=list)
