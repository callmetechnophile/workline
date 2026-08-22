"""Physics Service for feature extraction, reference thermal solving, and dataset generation."""

from typing import List, Optional
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.physics.dataset import ThermalDataset, ThermalDatasetGenerator
from backend.workline.pcb.physics.features import PhysicsFeatureEngine, PhysicsFeaturePoint
from backend.workline.pcb.physics.reference_solver import ReferenceThermalSolver, ThermalSolverResult
from backend.workline.pcb.services.pcb_service import PCBService, pcb_service


class PhysicsService:
    """Coordinates physics feature calculation, ground-truth reference solver runs, and dataset production."""

    def __init__(self, pcb_svc: Optional[PCBService] = None):
        self.pcb_svc = pcb_svc or pcb_service
        self.feature_engine = PhysicsFeatureEngine()
        self.reference_solver = ReferenceThermalSolver()
        self.dataset_generator = ThermalDatasetGenerator()

    async def extract_features(self, project_id: str, nx: int = 50, ny: int = 40) -> List[PhysicsFeaturePoint]:
        """Extract spatial physics feature vector across the PCB domain."""
        proj = await self.pcb_svc.get_pcb_project(project_id)
        if not proj:
            raise ValueError(f"PCB project '{project_id}' not found.")
        return self.feature_engine.extract_features(proj, nx=nx, ny=ny)

    async def solve_reference_thermal(self, project_id: str) -> ThermalSolverResult:
        """Run numerical reference solver for steady-state thermal distribution."""
        proj = await self.pcb_svc.get_pcb_project(project_id)
        if not proj:
            raise ValueError(f"PCB project '{project_id}' not found.")
        return self.reference_solver.solve(proj)

    async def generate_thermal_dataset(
        self, project_id: str, nx: int = 40, ny: int = 30
    ) -> ThermalDataset:
        """Constructs train/validation/test dataset for PINN training."""
        proj = await self.pcb_svc.get_pcb_project(project_id)
        if not proj:
            raise ValueError(f"PCB project '{project_id}' not found.")
        return self.dataset_generator.generate_dataset(proj)


# Global singleton physics service
physics_service = PhysicsService()
