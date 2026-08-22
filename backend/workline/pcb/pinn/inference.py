"""Fast batch PINN inference over 2D board coordinates."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.physics.features import PhysicsFeatureEngine
from backend.workline.pcb.pinn.model import PCBThermalPINN


class PINNInferenceResult(BaseModel):
    """Execution output from PINN forward temperature field prediction."""
    model_name: str = "PCB Thermal PINN (Physics-Informed Neural Network)"
    nx: int
    ny: int
    ambient_temperature: float
    predicted_peak_temperature: float
    predicted_min_temperature: float
    predicted_avg_temperature: float
    temperature_grid: List[List[float]] = Field(default_factory=list) # [ny, nx] in °C
    hotspots: List[Dict[str, Any]] = Field(default_factory=list)


class PINNInferenceEngine:
    """Evaluates temperature fields from candidate layouts rapidly via PINN forward pass."""

    def __init__(self, model: Optional[PCBThermalPINN] = None):
        self.model = model or PCBThermalPINN()
        self.feature_engine = PhysicsFeatureEngine()

    def predict_project_thermal_field(self, project: PCBProject, nx: int = 50, ny: int = 40) -> PINNInferenceResult:
        """
        Extracts physics features across the board and evaluates PINN predicted temperature grid.
        """
        board = project.board
        features = self.feature_engine.extract_features(project, nx=nx, ny=ny)

        X = np.array([
            [f.normalized_x, f.normalized_y, f.power_density_w_per_mm2, f.effective_conductivity, f.convection_coefficient, f.ambient_temperature, f.distance_to_board_edge / max(board.width, 1.0)]
            for f in features
        ], dtype=np.float64)

        t_amb = project.thermal.ambient_temperature
        t_scale = 50.0

        # Run forward pass
        norm_pred = self.model.predict(X)
        pred_deg = t_amb + (norm_pred * t_scale)

        grid = np.reshape(pred_deg, (ny, nx))

        peak_t = float(np.max(grid))
        min_t = float(np.min(grid))
        avg_t = float(np.mean(grid))

        hotspots = []
        for comp in project.components.values():
            gi = int(round((comp.x / max(board.width, 1.0)) * (nx - 1)))
            gj = int(round((comp.y / max(board.height, 1.0)) * (ny - 1)))
            gi = max(0, min(nx - 1, gi))
            gj = max(0, min(ny - 1, gj))
            ctemp = float(grid[gj, gi])
            if ctemp > t_amb + 10.0:
                hotspots.append({
                    "component": comp.reference_designator,
                    "x": comp.x,
                    "y": comp.y,
                    "predicted_temp": round(ctemp, 2),
                })

        return PINNInferenceResult(
            nx=nx,
            ny=ny,
            ambient_temperature=t_amb,
            predicted_peak_temperature=round(peak_t, 2),
            predicted_min_temperature=round(min_t, 2),
            predicted_avg_temperature=round(avg_t, 2),
            temperature_grid=[[round(float(val), 2) for val in row] for row in grid],
            hotspots=hotspots,
        )
