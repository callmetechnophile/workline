"""PCB Layer Stackup definition and dielectric sequence."""

from typing import List
from pydantic import BaseModel, Field
from backend.workline.pcb.models.layer import Layer, LayerType


class Stackup(BaseModel):
    """Multi-layer PCB Stackup assembly."""
    id: str = "stackup_default"
    name: str = "Standard 4-Layer FR4 Stackup"
    layers: List[Layer] = Field(default_factory=lambda: [
        Layer(id="L1", name="L1 Top Signal", type=LayerType.SIGNAL, order=1, thickness=0.035, copper_thickness=0.035),
        Layer(id="D1", name="Dielectric Core 1", type=LayerType.DIELECTRIC, order=2, thickness=0.500, material="FR4 Core", dielectric_constant=4.4),
        Layer(id="L2", name="L2 GND Plane", type=LayerType.GROUND, order=3, thickness=0.035, copper_thickness=0.035),
        Layer(id="D2", name="Prepreg Dielectric", type=LayerType.DIELECTRIC, order=4, thickness=0.460, material="FR4 Prepreg", dielectric_constant=4.2),
        Layer(id="L3", name="L3 Power Plane", type=LayerType.POWER, order=5, thickness=0.035, copper_thickness=0.035),
        Layer(id="D3", name="Dielectric Core 2", type=LayerType.DIELECTRIC, order=6, thickness=0.500, material="FR4 Core", dielectric_constant=4.4),
        Layer(id="L4", name="L4 Bottom Signal", type=LayerType.SIGNAL, order=7, thickness=0.035, copper_thickness=0.035),
    ])
    total_thickness: float = 1.6       # mm
