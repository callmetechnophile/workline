"""Thermal placement objective evaluating peak board and component temperatures."""

from typing import Dict, Optional, Tuple
import numpy as np
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.physics.reference_solver import ReferenceThermalSolver
from backend.workline.pcb.pinn.inference import PINNInferenceEngine


class ThermalPlacementObjective:
    """Evaluates peak thermal cost function: Cost = Peak_Temperature + Penalty(overheats)."""

    def __init__(
        self,
        pinn_engine: Optional[PINNInferenceEngine] = None,
        reference_solver: Optional[ReferenceThermalSolver] = None,
    ):
        self.pinn_engine = pinn_engine
        self.reference_solver = reference_solver or ReferenceThermalSolver(nx=30, ny=25, max_iter=400)

    def evaluate_cost(
        self, project: PCBProject, candidate_coords: Dict[str, Tuple[float, float]]
    ) -> float:
        """
        Creates a temporary project layout and evaluates peak temperature.
        """
        # Apply candidate coordinates to project components
        test_comps = {}
        for cid, comp in project.components.items():
            if cid in candidate_coords:
                cx, cy = candidate_coords[cid]
                test_comps[cid] = comp.model_copy(update={"x": cx, "y": cy})
            else:
                test_comps[cid] = comp

        test_proj = project.model_copy(update={"components": test_comps})

        # Use PINN if available, else reference solver
        if self.pinn_engine:
            res = self.pinn_engine.predict_project_thermal_field(test_proj, nx=30, ny=25)
            return res.predicted_peak_temperature
        else:
            ref_res = self.reference_solver.solve(test_proj)
            return ref_res.peak_temperature
