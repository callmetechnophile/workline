"""Physics Feature Engine extracting deterministic numerical spatial and physical features."""

import math
from typing import Any, Dict, List, Tuple
import numpy as np
from pydantic import BaseModel, Field

from backend.workline.pcb.models.project import PCBProject


class PhysicsFeaturePoint(BaseModel):
    """Calculated physical and geometric feature vector at a specific spatial location (x, y)."""
    x: float                           # Board x in mm
    y: float                           # Board y in mm
    normalized_x: float                # [0, 1]
    normalized_y: float                # [0, 1]
    z_layer_offset: float = 0.0        # mm

    # Physical & Thermal Parameters
    power_density_w_per_mm2: float = 0.0
    effective_conductivity: float = 18.5 # W/(m·K)
    convection_coefficient: float = 15.0 # W/(m2·K)
    ambient_temperature: float = 25.0  # °C

    # Geometric Proximities
    distance_to_nearest_heat_source: float = 999.0 # mm
    nearest_component_power: float = 0.0 # W
    local_component_density: float = 0.0 # Components per 100mm2
    distance_to_board_edge: float = 0.0 # mm

    # Conductor & Dielectric Parameters
    copper_plane_ratio: float = 0.65
    dielectric_constant: float = 4.4
    trace_density: float = 0.15


class PhysicsFeatureEngine:
    """Computes dense or mesh-aligned physics feature vectors deterministically."""

    def __init__(self):
        pass

    def extract_features(self, project: PCBProject, nx: int = 50, ny: int = 40) -> List[PhysicsFeaturePoint]:
        """
        Extracts spatial feature points across an Nx x Ny grid spanning the board.
        """
        board = project.board
        t_model = project.thermal
        comps = list(project.components.values())
        fps = project.footprints

        # Heat sources list: (cx, cy, w, h, power)
        heat_sources = []
        for comp in comps:
            tcomp = t_model.components.get(comp.id)
            power = tcomp.power_dissipation if tcomp else 0.05
            fp = fps.get(comp.footprint_id)
            bw = fp.body_width if fp else 5.0
            bh = fp.body_height if fp else 5.0
            heat_sources.append((comp.x, comp.y, bw, bh, power))

        eff_k = t_model.board_properties.effective_conductivity
        h_conv = t_model.board_properties.convection_coefficient
        t_amb = t_model.board_properties.ambient_temperature

        xs = np.linspace(0.0, board.width, nx)
        ys = np.linspace(0.0, board.height, ny)

        feature_points: List[PhysicsFeaturePoint] = []

        for y in ys:
            for x in xs:
                # Calculate localized power density
                local_power_density = 0.0
                min_dist = 999.0
                nearest_power = 0.0

                for (cx, cy, bw, bh, pwr) in heat_sources:
                    dx = abs(x - cx)
                    dy = abs(y - cy)
                    dist = math.hypot(x - cx, y - cy)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_power = pwr

                    # If inside component footprint bounding box
                    if dx <= (bw / 2.0) and dy <= (bh / 2.0):
                        area = max(bw * bh, 1.0)
                        local_power_density += (pwr / area)

                # Distance to closest board boundary edge
                edge_dist = min(x, board.width - x, y, board.height - y)

                # Component count within 15mm radius
                radius = 15.0
                local_comps = sum(1 for (cx, cy, _, _, _) in heat_sources if math.hypot(x - cx, y - cy) <= radius)
                local_density = local_comps / (math.pi * (radius ** 2) / 100.0)

                feature_points.append(
                    PhysicsFeaturePoint(
                        x=round(float(x), 3),
                        y=round(float(y), 3),
                        normalized_x=round(float(x / max(board.width, 1.0)), 4),
                        normalized_y=round(float(y / max(board.height, 1.0)), 4),
                        power_density_w_per_mm2=round(float(local_power_density), 5),
                        effective_conductivity=eff_k,
                        convection_coefficient=h_conv,
                        ambient_temperature=t_amb,
                        distance_to_nearest_heat_source=round(float(min_dist), 2),
                        nearest_component_power=round(float(nearest_power), 3),
                        local_component_density=round(float(local_density), 3),
                        distance_to_board_edge=round(float(edge_dist), 2),
                    )
                )

        return feature_points
