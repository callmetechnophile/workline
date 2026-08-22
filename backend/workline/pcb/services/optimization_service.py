"""PCB Optimization Service orchestrating PINN training, inference, and thermal placement optimization."""

from typing import Any, Dict, Optional, Tuple

from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.optimization.objective import ThermalPlacementObjective
from backend.workline.pcb.optimization.optimizer import OptimizationResult, ThermalPlacementOptimizer
from backend.workline.pcb.pinn.inference import PINNInferenceEngine, PINNInferenceResult
from backend.workline.pcb.pinn.model import PCBThermalPINN
from backend.workline.pcb.pinn.trainer import PINNTrainer, TrainingRunResult
from backend.workline.pcb.services.pcb_service import PCBService, pcb_service
from backend.workline.pcb.services.physics_service import PhysicsService, physics_service


class PCBOptimizationService:
    """Manages PINN model training, fast thermal inference, and automated layout optimization."""

    def __init__(
        self,
        pcb_svc: Optional[PCBService] = None,
        physics_svc: Optional[PhysicsService] = None,
    ):
        self.pcb_svc = pcb_svc or pcb_service
        self.physics_svc = physics_svc or physics_service
        self._trained_models: Dict[str, PCBThermalPINN] = {}
        self._training_results: Dict[str, TrainingRunResult] = {}

    async def train_pinn(
        self,
        project_id: str,
        epochs: int = 50,
        learning_rate: float = 0.008,
    ) -> TrainingRunResult:
        """Generates ground-truth dataset and trains the PCB Thermal PINN."""
        # 1. Generate Dataset
        dataset = await self.physics_svc.generate_thermal_dataset(project_id)

        # 2. Train PINN
        trainer = PINNTrainer(epochs=epochs, learning_rate=learning_rate)
        model, result = trainer.train(dataset)

        self._trained_models[project_id] = model
        self._trained_models[result.model_id] = model
        self._training_results[project_id] = result
        self._training_results[result.model_id] = result

        return result

    async def run_pinn_inference(
        self, project_id: str, nx: int = 50, ny: int = 40
    ) -> PINNInferenceResult:
        """Evaluates PINN predicted 2D thermal field."""
        proj = await self.pcb_svc.get_pcb_project(project_id)
        if not proj:
            raise ValueError(f"PCB project '{project_id}' not found.")

        model = self._trained_models.get(project_id)
        if not model:
            # Train lightweight default model if not yet trained
            train_res = await self.train_pinn(project_id, epochs=25)
            model = self._trained_models[project_id]

        inference_engine = PINNInferenceEngine(model=model)
        return inference_engine.predict_project_thermal_field(proj, nx=nx, ny=ny)

    async def optimize_placement(
        self, project_id: str, max_iterations: int = 50
    ) -> Tuple[PCBProject, OptimizationResult]:
        """Runs thermal placement optimization loop and saves updated placement."""
        proj = await self.pcb_svc.get_pcb_project(project_id)
        if not proj:
            raise ValueError(f"PCB project '{project_id}' not found.")

        model = self._trained_models.get(project_id)
        pinn_engine = PINNInferenceEngine(model=model) if model else None
        objective = ThermalPlacementObjective(pinn_engine=pinn_engine)

        optimizer = ThermalPlacementOptimizer(objective=objective, max_iterations=max_iterations)
        updated_proj, result = optimizer.optimize(proj)

        # Persist updated project
        await self.pcb_svc.update_pcb_project(updated_proj)
        return updated_proj, result

    def get_latest_metrics(self, project_id: str) -> Optional[TrainingRunResult]:
        """Fetch latest PINN training metrics."""
        return self._training_results.get(project_id)


# Global singleton optimization service
pcb_optimization_service = PCBOptimizationService()
