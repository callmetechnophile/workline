"""Simplified numerical reference thermal solver for 2D steady-state heat diffusion on a PCB."""

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from backend.workline.pcb.models.project import PCBProject


class ThermalSolverResult(BaseModel):
    """Execution output from numerical reference thermal solver."""
    solver_name: str = "SIMPLIFIED REFERENCE SOLVER"
    nx: int
    ny: int
    width_mm: float
    height_mm: float
    dx_mm: float
    dy_mm: float
    ambient_temperature: float
    peak_temperature: float
    min_temperature: float
    average_temperature: float
    grid_temperature: List[List[float]] = Field(default_factory=list) # 2D array [ny, nx] in °C
    iterations: int
    converged: bool
    hotspots: List[Dict[str, Any]] = Field(default_factory=list)


class ReferenceThermalSolver:
    """
    SIMPLIFIED REFERENCE SOLVER
    Solves the 2D steady-state heat equation with convective surface/edge losses and localized component heat sources.
    Used for ground-truth data generation and PINN validation.
    """

    def __init__(self, nx: int = 50, ny: int = 40, max_iter: int = 1500, tolerance: float = 1e-4):
        self.nx = nx
        self.ny = ny
        self.max_iter = max_iter
        self.tolerance = tolerance

    def solve(self, project: PCBProject) -> ThermalSolverResult:
        """
        Solves the steady-state thermal distribution:
        -k_eff * (d2T/dx2 + d2T/dy2) + (2*h/t)*(T - T_inf) = Q(x,y)
        """
        board = project.board
        t_model = project.thermal

        w_mm = board.width
        h_mm = board.height
        t_board_m = board.thickness * 1e-3 # Convert mm to m

        dx_m = (w_mm * 1e-3) / (self.nx - 1)
        dy_m = (h_mm * 1e-3) / (self.ny - 1)

        k_eff = t_model.board_properties.effective_conductivity # W/(m·K)
        h_conv = t_model.board_properties.convection_coefficient # W/(m2·K)
        t_amb = t_model.board_properties.ambient_temperature # °C

        # 1. Build volumetric heat generation grid Q(x,y) in W/m3
        Q = np.zeros((self.ny, self.nx), dtype=np.float64)

        xs = np.linspace(0.0, w_mm, self.nx)
        ys = np.linspace(0.0, h_mm, self.ny)

        for comp in project.components.values():
            tcomp = t_model.components.get(comp.id)
            power_w = tcomp.power_dissipation if tcomp else 0.05
            fp = project.footprints.get(comp.footprint_id)
            bw = fp.body_width if fp else 5.0
            bh = fp.body_height if fp else 5.0

            # Component footprint area
            area_m2 = max((bw * 1e-3) * (bh * 1e-3), 1e-6)
            vol_m3 = area_m2 * t_board_m
            q_vol = power_w / vol_m3 # W/m3

            # Distribute onto grid using Gaussian profile centered at (comp.x, comp.y)
            sigma_x = max((bw / 2.5), 1.0) # mm
            sigma_y = max((bh / 2.5), 1.0) # mm

            for j, y_val in enumerate(ys):
                for i, x_val in enumerate(xs):
                    dist_sq = ((x_val - comp.x) / sigma_x) ** 2 + ((y_val - comp.y) / sigma_y) ** 2
                    if dist_sq < 9.0: # 3-sigma bounding box
                        weight = math.exp(-0.5 * dist_sq)
                        Q[j, i] += q_vol * weight

        # 2. Iterative Finite-Difference Solution (Successive Over-Relaxation)
        T = np.full((self.ny, self.nx), t_amb, dtype=np.float64)
        omega = 1.35 # Over-relaxation factor

        coeff_x = k_eff / (dx_m ** 2)
        coeff_y = k_eff / (dy_m ** 2)
        coeff_conv = (2.0 * h_conv) / t_board_m
        denom = 2.0 * coeff_x + 2.0 * coeff_y + coeff_conv

        converged = False
        iter_count = 0

        for it in range(self.max_iter):
            max_diff = 0.0
            for j in range(1, self.ny - 1):
                for i in range(1, self.nx - 1):
                    t_new = (
                        coeff_x * (T[j, i + 1] + T[j, i - 1])
                        + coeff_y * (T[j + 1, i] + T[j - 1, i])
                        + coeff_conv * t_amb
                        + Q[j, i]
                    ) / denom

                    t_sor = T[j, i] + omega * (t_new - T[j, i])
                    diff = abs(t_sor - T[j, i])
                    if diff > max_diff:
                        max_diff = diff
                    T[j, i] = t_sor

            # Apply Robin boundary conditions on all 4 board edges: -k dT/dn = h(T - T_amb)
            # Left & Right edges
            bi_x = (h_conv * dx_m) / k_eff
            T[:, 0] = (T[:, 1] + bi_x * t_amb) / (1.0 + bi_x)
            T[:, -1] = (T[:, -2] + bi_x * t_amb) / (1.0 + bi_x)

            # Top & Bottom edges
            bi_y = (h_conv * dy_m) / k_eff
            T[0, :] = (T[1, :] + bi_y * t_amb) / (1.0 + bi_y)
            T[-1, :] = (T[-2, :] + bi_y * t_amb) / (1.0 + bi_y)

            iter_count += 1
            if max_diff < self.tolerance:
                converged = True
                break

        # 3. Compile output results
        peak_t = float(np.max(T))
        min_t = float(np.min(T))
        avg_t = float(np.mean(T))

        # Detect hotspot components
        hotspots = []
        for comp in project.components.values():
            # Interpolate temperature at component coordinates
            grid_i = int(round((comp.x / max(w_mm, 1.0)) * (self.nx - 1)))
            grid_j = int(round((comp.y / max(h_mm, 1.0)) * (self.ny - 1)))
            grid_i = max(0, min(self.nx - 1, grid_i))
            grid_j = max(0, min(self.ny - 1, grid_j))

            c_temp = float(T[grid_j, grid_i])
            if c_temp > t_amb + 10.0:
                hotspots.append({
                    "component": comp.reference_designator,
                    "x": comp.x,
                    "y": comp.y,
                    "temperature": round(c_temp, 2),
                })

        return ThermalSolverResult(
            nx=self.nx,
            ny=self.ny,
            width_mm=w_mm,
            height_mm=h_mm,
            dx_mm=round(float(dx_m * 1e3), 3),
            dy_mm=round(float(dy_m * 1e3), 3),
            ambient_temperature=t_amb,
            peak_temperature=round(peak_t, 2),
            min_temperature=round(min_t, 2),
            average_temperature=round(avg_t, 2),
            grid_temperature=[[round(float(val), 2) for val in row] for row in T],
            iterations=iter_count,
            converged=converged,
            hotspots=hotspots,
        )
