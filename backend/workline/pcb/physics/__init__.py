"""PCB Physics Engine package."""

from backend.workline.pcb.physics.boundary_conditions import BoundaryType, ThermalBoundaryConditions
from backend.workline.pcb.physics.dataset import ThermalDataset, ThermalDatasetGenerator, ThermalDatasetSample
from backend.workline.pcb.physics.features import PhysicsFeatureEngine, PhysicsFeaturePoint
from backend.workline.pcb.physics.geometry import HeatSourceGeometry, SpatialMesh2D
from backend.workline.pcb.physics.reference_solver import ReferenceThermalSolver, ThermalSolverResult
from backend.workline.pcb.physics.solver import PhysicsProblem

__all__ = [
    "SpatialMesh2D",
    "HeatSourceGeometry",
    "BoundaryType",
    "ThermalBoundaryConditions",
    "PhysicsFeaturePoint",
    "PhysicsFeatureEngine",
    "PhysicsProblem",
    "ReferenceThermalSolver",
    "ThermalSolverResult",
    "ThermalDatasetSample",
    "ThermalDataset",
    "ThermalDatasetGenerator",
]
