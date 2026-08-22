"""Board geometry, outline, keepouts, mounting holes, and material specifications."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class BoardShape(str, Enum):
    """Board shape geometry types."""
    RECTANGLE = "RECTANGLE"
    POLYGON = "POLYGON"
    CIRCULAR = "CIRCULAR"


class MountingHole(BaseModel):
    """Mechanical mounting hole."""
    id: str
    x: float
    y: float
    diameter: float = 3.2
    plated: bool = True


class Cutout(BaseModel):
    """Board internal cutout or routing slot."""
    id: str
    x: float
    y: float
    width: float
    height: float


class Keepout(BaseModel):
    """Restricted zone for component placement, routing, or copper pour."""
    id: str
    name: str = "Keepout"
    x: float
    y: float
    width: float
    height: float
    layers: List[str] = Field(default_factory=lambda: ["ALL"])
    type: str = "PLACEMENT_AND_ROUTING"  # PLACEMENT, ROUTING, COPPER, PLACEMENT_AND_ROUTING


class Board(BaseModel):
    """Authoritative physical PCB Board specification."""
    width: float = 80.0                # mm
    height: float = 60.0               # mm
    thickness: float = 1.6             # mm (standard 1.6mm)
    shape: BoardShape = BoardShape.RECTANGLE
    material: str = "FR4"
    substrate: str = "Standard High-Tg FR4 (Tg=170°C)"
    copper_weight: float = 1.0         # oz (35um copper)
    layer_count: int = 4

    mounting_holes: List[MountingHole] = Field(default_factory=list)
    cutouts: List[Cutout] = Field(default_factory=list)
    keepouts: List[Keepout] = Field(default_factory=list)
