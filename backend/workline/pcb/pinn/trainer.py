"""PINN Training Loop with backpropagation, Adam optimizer, loss logging, and validation."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from backend.workline.pcb.physics.dataset import ThermalDataset
from backend.workline.pcb.pinn.checkpoints import CheckpointManager, ModelCheckpointMetadata
from backend.workline.pcb.pinn.loss import PINNLossCalculator, PINNLossComponents
from backend.workline.pcb.pinn.metrics import PINNMetricsCalculator, PINNValidationMetrics
from backend.workline.pcb.pinn.model import PCBThermalPINN


class EpochLogItem(BaseModel):
    """Training progress log entry per epoch."""
    epoch: int
    data_loss: float
    physics_loss: float
    boundary_loss: float
    total_loss: float
    val_mae: Optional[float] = None


class TrainingRunResult(BaseModel):
    """Complete summary of PINN training execution."""
    model_id: str
    epochs_completed: int
    final_train_loss: float
    validation_metrics: PINNValidationMetrics
    epoch_history: List[EpochLogItem] = Field(default_factory=list)
    metadata: ModelCheckpointMetadata


class PINNTrainer:
    """Orchestrates PINN model training, analytical backpropagation, and checkpointing."""

    def __init__(
        self,
        learning_rate: float = 0.008,
        epochs: int = 50,
        batch_size: int = 64,
        random_seed: int = 42,
    ):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.random_seed = random_seed
        self.loss_calc = PINNLossCalculator()
        self.checkpoint_manager = CheckpointManager()

    def train(
        self,
        dataset: ThermalDataset,
        model: Optional[PCBThermalPINN] = None,
    ) -> Tuple[PCBThermalPINN, TrainingRunResult]:
        """Trains the PINN model on dataset training samples and validates on validation samples."""
        if not model:
            model = PCBThermalPINN(
                input_dim=7,
                hidden_dim=48,
                hidden_layers=3,
                learning_rate=self.learning_rate,
                random_seed=self.random_seed,
            )

        # 1. Prepare Arrays
        train_samples = [s for s in dataset.samples if s.split == "TRAIN"]
        val_samples = [s for s in dataset.samples if s.split == "VALIDATION"]
        if not val_samples:
            val_samples = train_samples

        def _to_arrays(samples):
            X = np.array([
                [s.x_norm, s.y_norm, s.power_density, s.effective_k, s.convection_h, s.ambient_temp, s.edge_distance_norm]
                for s in samples
            ], dtype=np.float64)
            y_norm = np.array([[s.normalized_temperature] for s in samples], dtype=np.float64)
            y_celsius = np.array([[s.temperature_celsius] for s in samples], dtype=np.float64)
            return X, y_norm, y_celsius

        X_train, y_train_norm, y_train_deg = _to_arrays(train_samples)
        X_val, y_val_norm, y_val_deg = _to_arrays(val_samples)

        history: List[EpochLogItem] = []
        n_samples = len(X_train)

        # 2. Training Loop (Mini-batch SGD with Momentum / Adam)
        t_amb = dataset.samples[0].ambient_temp if dataset.samples else 25.0
        t_scale = 50.0

        for epoch in range(1, self.epochs + 1):
            # Shuffle indices
            perm = np.random.permutation(n_samples)
            X_shuffled = X_train[perm]
            y_shuffled = y_train_norm[perm]

            for start in range(0, n_samples, self.batch_size):
                end = min(start + self.batch_size, n_samples)
                xb = X_shuffled[start:end]
                yb = y_shuffled[start:end]

                # Forward pass
                pred, acts, preacts = model.forward(xb)

                # Backprop gradient: dLoss/dOutput
                grad_out = 2.0 * (pred - yb) / len(xb)

                # Backpropagate through layers
                delta = grad_out
                for layer_idx in range(len(model.weights) - 1, -1, -1):
                    in_act = acts[layer_idx]
                    grad_w = np.dot(in_act.T, delta)
                    grad_b = np.sum(delta, axis=0, keepdims=True)

                    if layer_idx > 0:
                        prev_z = preacts[layer_idx - 1]
                        prev_act = acts[layer_idx]
                        delta = np.dot(delta, model.weights[layer_idx].T) * model._dact(prev_act)

                    # Update parameters (Adam update)
                    model.t_adam += 1
                    beta1, beta2, eps = 0.9, 0.999, 1e-8

                    model.m_w[layer_idx] = beta1 * model.m_w[layer_idx] + (1 - beta1) * grad_w
                    model.v_w[layer_idx] = beta2 * model.v_w[layer_idx] + (1 - beta2) * (grad_w ** 2)
                    m_hat_w = model.m_w[layer_idx] / (1 - beta1 ** model.t_adam)
                    v_hat_w = model.v_w[layer_idx] / (1 - beta2 ** model.t_adam)
                    model.weights[layer_idx] -= model.learning_rate * m_hat_w / (np.sqrt(v_hat_w) + eps)

                    model.m_b[layer_idx] = beta1 * model.m_b[layer_idx] + (1 - beta1) * grad_b
                    model.v_b[layer_idx] = beta2 * model.v_b[layer_idx] + (1 - beta2) * (grad_b ** 2)
                    m_hat_b = model.m_b[layer_idx] / (1 - beta1 ** model.t_adam)
                    v_hat_b = model.v_b[layer_idx] / (1 - beta2 ** model.t_adam)
                    model.biases[layer_idx] -= model.learning_rate * m_hat_b / (np.sqrt(v_hat_b) + eps)

            # Evaluate epoch loss
            full_pred = model.predict(X_train)
            losses = self.loss_calc.compute_losses(full_pred, y_train_norm, X_train)

            # Validation metrics
            val_pred_norm = model.predict(X_val)
            val_pred_deg = t_amb + (val_pred_norm * t_scale)
            val_metrics = PINNMetricsCalculator.evaluate(val_pred_deg, y_val_deg)

            history.append(
                EpochLogItem(
                    epoch=epoch,
                    data_loss=losses.data_loss,
                    physics_loss=losses.physics_loss,
                    boundary_loss=losses.boundary_loss,
                    total_loss=losses.total_loss,
                    val_mae=val_metrics.mae_celsius,
                )
            )

        # 3. Final Validation
        val_pred_norm = model.predict(X_val)
        val_pred_deg = t_amb + (val_pred_norm * t_scale)
        final_metrics = PINNMetricsCalculator.evaluate(val_pred_deg, y_val_deg)

        # 4. Save Checkpoint
        state_dict = model.get_state_dict()
        training_config = {
            "epochs": self.epochs,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "random_seed": self.random_seed,
        }
        meta = self.checkpoint_manager.save_checkpoint(
            project_id=dataset.project_id,
            dataset_id=dataset.dataset_id,
            state_dict=state_dict,
            metrics=final_metrics,
            training_config=training_config,
        )

        res = TrainingRunResult(
            model_id=meta.model_id,
            epochs_completed=self.epochs,
            final_train_loss=history[-1].total_loss,
            validation_metrics=final_metrics,
            epoch_history=history,
            metadata=meta,
        )

        return model, res
