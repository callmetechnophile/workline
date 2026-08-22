"""PCB physical geometry and spatial heat source representation."""

from typing import Dict, List, Tuple
import numpy as np
from pydantic import BaseModel, Field


class HeatSourceGeometry(BaseModel):
    """Component localized heat generation zone."""
    component_id: str
    reference_designator: str
    center_x: float                   # mm
    center_y: float                   # mm
    width: float                      # mm
    height: float                     # mm
    power_watts: float                # W
    power_density_w_per_mm2: float    # W/mm2


class SpatialMesh2D(BaseModel):
    """Discretized 2D grid for board domain."""
    width_mm: float
    height_mm: float
    nx: int = 50
    ny: int = 40
    dx_mm: float = 1.0
    dy_mm: float = 1.0
