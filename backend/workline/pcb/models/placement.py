"""Component placement, spatial coordinates, and design zones."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ZoneType(str, Enum):
    """Functional partitioning zones for layout organization."""
    THERMAL_ZONE = "thermal_zone"
    POWER_ZONE = "power_zone"
    ANALOG_ZONE = "analog_zone"
    DIGITAL_ZONE = "digital_zone"
    HIGH_SPEED_ZONE = "high_speed_zone"


class PlacementZone(BaseModel):
    """Dedicated rectangular layout region on board."""
    id: str
    name: str
    zone_type: ZoneType
    x: float
    y: float
    width: float
    height: float


class ComponentPlacement(BaseModel):
    """Component spatial coordinates on the board."""
    component_id: str
    reference_designator: str
    x: float
    y: float
    rotation: float = 0.0
    layer: str = "TOP"
    locked: bool = False


class Placement(BaseModel):
    """Complete layout placement state."""
    placements: Dict[str, ComponentPlacement] = Field(default_factory=dict)
    zones: List[PlacementZone] = Field(default_factory=list)
    version: int = 1
