"""PCB Component model referencing canonical Workline component record."""

from typing import List, Optional
from pydantic import BaseModel, Field
from backend.workline.pcb.models.pin import Pin


class PCBComponent(BaseModel):
    """
    PCB-specific component instance.
    References the authoritative Workline component without duplicating catalog specifications.
    """
    id: str                            # Unique instance ID, e.g. "pcb_comp_u1"
    component_id: str                  # Reference to canonical Component in Workline (e.g. "component:espressif_esp32_s3_wroom_1")
    reference_designator: str          # e.g. "U1", "R1", "C1", "D1", "J1"
    value: str = ""                    # e.g. "ESP32-S3", "10k", "100nF", "TPS62130"
    footprint_id: str                  # Reference to Footprint ID

    # Physical Placement on Board
    x: float = 0.0                     # Board coordinates in mm
    y: float = 0.0
    rotation: float = 0.0              # Degrees (0, 90, 180, 270)
    layer: str = "TOP"                 # TOP or BOTTOM

    mounting_type: str = "SMD"         # SMD or THROUGH_HOLE
    orientation: str = "STANDARD"

    locked: bool = False               # If True, optimizer and placement engine must not move this component

    # Associated pins
    pins: List[Pin] = Field(default_factory=list)
