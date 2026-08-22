"""Normalized PCB component footprint, pad layout, and courtyard representation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Pad(BaseModel):
    """Component land pattern pad."""
    number: int
    name: Optional[str] = None
    x: float                           # Relative to footprint center in mm
    y: float
    width: float = 1.0                 # mm
    height: float = 1.0                # mm
    shape: str = "RECTANGULAR"         # RECTANGULAR, CIRCULAR, OVAL
    layer: str = "TOP"                 # TOP, BOTTOM, THROUGH_HOLE
    net_id: Optional[str] = None


class Footprint(BaseModel):
    """Normalized standard PCB package footprint."""
    id: str
    name: str                          # e.g., "QFN-32", "SOIC-8", "0805", "SOT-223", "ESP32-S3-WROOM"
    package: str
    body_width: float                  # mm
    body_height: float                 # mm

    pads: List[Pad] = Field(default_factory=list)
    courtyard_width: Optional[float] = None
    courtyard_height: Optional[float] = None
    keepout_margin: float = 0.5        # mm
    origin: str = "CENTER"
