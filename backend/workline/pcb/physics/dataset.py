"""Thermal physics dataset generation with explicit train/validation/test splits."""

from datetime import datetime, timezone
import random
from typing import Any, Dict, List, Optional
import uuid
import numpy as np
from pydantic import BaseModel, Field

from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.physics.features import PhysicsFeatureEngine, PhysicsFeaturePoint
from backend.workline.pcb.physics.reference_solver import ReferenceThermalSolver


class ThermalDatasetSample(BaseModel):
    """Individual spatial point sample for PINN training and validation."""
    sample_id: str
    project_id: str
    split: str                         # TRAIN, VALIDATION, TEST

    # Inputs
    x_norm: float
    y_norm: float
    power_density: float
    effective_k: float
    convection_h: float
    ambient_temp: float
    edge_distance_norm: float

    # Ground Truth Target from Reference Solver
    temperature_celsius: float
    normalized_temperature: float


class ThermalDataset(BaseModel):
    """Complete structured dataset with metadata and provenance."""
    dataset_id: str
    project_id: str
    version: int = 1
    source: str = "SIMPLIFIED REFERENCE SOLVER"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    total_samples: int
    train_count: int
    validation_count: int
    test_count: int

    samples: List[ThermalDatasetSample] = Field(default_factory=list)


class ThermalDatasetGenerator:
    """Generates training, validation, and test datasets by coupling PhysicsFeatureEngine and ReferenceThermalSolver."""

    def __init__(self, nx: int = 40, ny: int = 30, random_seed: int = 42):
        self.nx = nx
        self.ny = ny
        self.random_seed = random_seed
        self.feature_engine = PhysicsFeatureEngine()
        self.reference_solver = ReferenceThermalSolver(nx=nx, ny=ny)

    def generate_dataset(self, project: PCBProject, train_ratio: float = 0.70, val_ratio: float = 0.15) -> ThermalDataset:
        """Runs the reference solver and packages ground-truth samples with explicit splits."""
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

        # 1. Run Reference Solver
        ref_res = self.reference_solver.solve(project)
        temp_grid = np.array(ref_res.grid_temperature) # [ny, nx]

        # 2. Extract Feature Points
        features = self.feature_engine.extract_features(project, nx=self.nx, ny=self.ny)

        samples: List[ThermalDatasetSample] = []
        sample_idx = 0

        # Normalization factors
        t_min = ref_res.ambient_temperature
        t_max = max(ref_res.peak_temperature, t_min + 50.0)

        for feat in features:
            grid_i = int(round(feat.normalized_x * (self.nx - 1)))
            grid_j = int(round(feat.normalized_y * (self.ny - 1)))
            grid_i = max(0, min(self.nx - 1, grid_i))
            grid_j = max(0, min(self.ny - 1, grid_j))

            temp = float(temp_grid[grid_j, grid_i])
            temp_norm = (temp - t_min) / max(t_max - t_min, 1e-4)

            # Assign split
            r = random.random()
            if r < train_ratio:
                split_name = "TRAIN"
            elif r < (train_ratio + val_ratio):
                split_name = "VALIDATION"
            else:
                split_name = "TEST"

            samples.append(
                ThermalDatasetSample(
                    sample_id=f"samp_{sample_idx}",
                    project_id=project.project_id,
                    split=split_name,
                    x_norm=feat.normalized_x,
                    y_norm=feat.normalized_y,
                    power_density=feat.power_density_w_per_mm2,
                    effective_k=feat.effective_conductivity,
                    convection_h=feat.convection_coefficient,
                    ambient_temp=feat.ambient_temperature,
                    edge_distance_norm=feat.distance_to_board_edge / max(project.board.width, 1.0),
                    temperature_celsius=round(temp, 2),
                    normalized_temperature=round(temp_norm, 4),
                )
            )
            sample_idx += 1

        n_train = sum(1 for s in samples if s.split == "TRAIN")
        n_val = sum(1 for s in samples if s.split == "VALIDATION")
        n_test = sum(1 for s in samples if s.split == "TEST")

        return ThermalDataset(
            dataset_id=f"thermal_ds_{uuid.uuid4().hex[:8]}",
            project_id=project.project_id,
            version=1,
            total_samples=len(samples),
            train_count=n_train,
            validation_count=n_val,
            test_count=n_test,
            samples=samples,
        )
