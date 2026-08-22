"""PCB Thermal Physics-Informed Neural Network (PINN) package."""

from backend.workline.pcb.pinn.checkpoints import CheckpointManager, ModelCheckpointMetadata
from backend.workline.pcb.pinn.inference import PINNInferenceEngine, PINNInferenceResult
from backend.workline.pcb.pinn.loss import PINNLossCalculator, PINNLossComponents
from backend.workline.pcb.pinn.metrics import PINNMetricsCalculator, PINNValidationMetrics
from backend.workline.pcb.pinn.model import PCBThermalPINN
from backend.workline.pcb.pinn.trainer import EpochLogItem, PINNTrainer, TrainingRunResult

__all__ = [
    "PCBThermalPINN",
    "PINNLossCalculator",
    "PINNLossComponents",
    "PINNMetricsCalculator",
    "PINNValidationMetrics",
    "CheckpointManager",
    "ModelCheckpointMetadata",
    "PINNTrainer",
    "EpochLogItem",
    "TrainingRunResult",
    "PINNInferenceEngine",
    "PINNInferenceResult",
]
