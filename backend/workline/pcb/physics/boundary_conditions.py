"""Thermal boundary conditions for PCB edges and surface convection."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class BoundaryType(str, Enum):
    """Types of thermal boundary conditions."""
    CONVECTIVE_ROBIN = "CONVECTIVE_ROBIN" # -k dT/dn = h(T - T_inf)
    INSULATED_NEUMANN = "INSULATED_NEUMANN" # dT/dn = 0
    FIXED_DIRICHLET = "FIXED_DIRICHLET"   # T = T_fixed


class ThermalBoundaryConditions(BaseModel):
    """Specification of boundary behavior across the 4 board edges and top/bottom faces."""
    ambient_temperature: float = 25.0  # °C (T_infinity)
    convection_coefficient: float = 15.0 # W/(m2·K) natural convection
    edge_type: BoundaryType = BoundaryType.CONVECTIVE_ROBIN
    top_face_type: BoundaryType = BoundaryType.CONVECTIVE_ROBIN
    bottom_face_type: BoundaryType = BoundaryType.CONVECTIVE_ROBIN
    fixed_edge_temp: Optional[float] = None
