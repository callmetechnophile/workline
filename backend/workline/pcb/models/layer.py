"""PCB Layer specifications and dielectric/conductor properties."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class LayerType(str, Enum):
    """PCB layer physical and electrical purpose."""
    SIGNAL = "SIGNAL"
    POWER = "POWER"
    GROUND = "GROUND"
    DIELECTRIC = "DIELECTRIC"
    MECHANICAL = "MECHANICAL"


class Layer(BaseModel):
    """Individual physical or copper layer in stackup."""
    id: str                            # e.g. "layer_top", "layer_in1_gnd"
    name: str                          # e.g. "L1 (Top Signal)", "L2 (GND Plane)"
    type: LayerType
    order: int                         # 1-indexed (top to bottom)
    thickness: float = 0.035           # mm (35um for 1oz copper)
    material: str = "Copper"
    dielectric_constant: float = 4.4   # Er (4.4 for FR4)
    loss_tangent: float = 0.02
    copper_thickness: float = 0.035    # mm


from backend.workline.pcb.models.stackup import Stackup
LayerStackup = Stackup
