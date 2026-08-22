"""Physics Problem abstraction for Steady-State PCB Thermal Distribution."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class PhysicsProblem(BaseModel):
    """
    Formal mathematical definition of a physical governing PDE problem.
    Phase 6 implements: Steady-State PCB Thermal Distribution.
    """
    name: str = "Steady-State PCB Thermal Distribution"
    problem_id: str = "thermal_diffusion_2d"
    governing_equation: str = "-k_eff * (d2T/dx2 + d2T/dy2) = Q(x,y) - (2*h/t)*(T - T_inf)"
    domain: str = "2D Composite PCB Plane [0, W] x [0, H]"
    inputs: List[str] = Field(default_factory=lambda: [
        "x", "y", "power_density", "effective_k", "convection_h", "ambient_temp", "distance_to_edge"
    ])
    outputs: List[str] = Field(default_factory=lambda: ["temperature_celsius"])
    boundary_conditions: str = "Robin Convective Boundary Conditions on edges and faces"
    initial_conditions: str = "T(x,y) = T_ambient (25°C)"
    normalization: Dict[str, Any] = Field(default_factory=lambda: {
        "x_scale": 1.0,
        "y_scale": 1.0,
        "temp_shift": 25.0,
        "temp_scale": 100.0,
    })
    loss_weights: Dict[str, float] = Field(default_factory=lambda: {
        "data": 1.0,
        "physics": 0.1,
        "boundary": 0.5,
        "constraint": 0.05,
    })
