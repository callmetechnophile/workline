"""PCB Thermal physics model (SIMPLIFIED THERMAL MODEL)."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ThermalComponent(BaseModel):
    """Component thermal dissipation and package junction characteristics."""
    component_id: str                  # Reference designator / PCBComponent id
    power_dissipation: float = 0.05    # Watts (e.g. 0.8W for regulator, 0.35W for MCU)
    thermal_resistance_jc: float = 25.0 # °C/W (Junction-to-Case)
    thermal_resistance_ja: float = 45.0 # °C/W (Junction-to-Ambient)
    max_junction_temperature: float = 125.0 # °C
    ambient_temperature: float = 25.0  # °C
    package_type: str = "SMD"


class BoardThermalProperties(BaseModel):
    """Board substrate and copper plane dissipation parameters."""
    ambient_temperature: float = 25.0  # °C
    material: str = "FR4"
    thermal_conductivity_fr4: float = 0.3 # W/(m·K)
    thermal_conductivity_copper: float = 390.0 # W/(m·K)
    effective_conductivity: float = 18.5 # W/(m·K) (Composite in-plane 4-layer FR4 + copper)
    convection_coefficient: float = 15.0 # W/(m2·K) natural convection
    copper_area_ratio: float = 0.65    # Fraction of board covered by copper planes
    thermal_vias_count: int = 0
    heatsinks_attached: List[str] = Field(default_factory=list)


class ThermalModel(BaseModel):
    """
    Simplified steady-state thermal representation.
    Label: SIMPLIFIED THERMAL MODEL. Not a full CFD/FEM fluid solver.
    """
    model_type: str = "SIMPLIFIED THERMAL MODEL"
    board_properties: BoardThermalProperties = Field(default_factory=BoardThermalProperties)
    components: Dict[str, ThermalComponent] = Field(default_factory=dict)
    peak_predicted_temperature: float = 25.0
    ambient_temperature: float = 25.0
    hotspots: List[str] = Field(default_factory=list)
    has_overheated_component: bool = False


ThermalModelMetadata = ThermalModel
