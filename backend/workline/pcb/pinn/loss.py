"""Physics-Informed Loss Functions combining Data Loss, PDE Residuals, and Boundary Conditions."""

from typing import Dict, Tuple
import numpy as np
from pydantic import BaseModel


class PINNLossComponents(BaseModel):
    """Decomposed individual loss components."""
    data_loss: float
    physics_loss: float
    boundary_loss: float
    total_loss: float


class PINNLossCalculator:
    """
    Computes modular loss objectives:
    L_total = lambda_data * L_data + lambda_physics * L_physics + lambda_boundary * L_boundary
    """

    def __init__(
        self,
        lambda_data: float = 1.0,
        lambda_physics: float = 0.15,
        lambda_boundary: float = 0.20,
    ):
        self.lambda_data = lambda_data
        self.lambda_physics = lambda_physics
        self.lambda_boundary = lambda_boundary

    def compute_losses(
        self,
        y_pred: np.ndarray,
        y_true: np.ndarray,
        X_inputs: np.ndarray,
    ) -> PINNLossComponents:
        """
        Calculates data, physics, and boundary losses from batch inputs and predictions.
        X_inputs columns: [x_norm, y_norm, power_density, effective_k, convection_h, ambient_temp, edge_dist_norm]
        """
        # 1. Data Loss: Mean Squared Error vs Reference Solver
        data_err = y_pred - y_true
        l_data = float(np.mean(data_err ** 2))

        # 2. Physics Loss: Simplified 2D Heat Equation Residual
        # Residual = |k * Lap(T) + Q - 2h/t*(T - T_amb)|
        q_power = X_inputs[:, 2:3] # Power density
        eff_k = X_inputs[:, 3:4]
        h_conv = X_inputs[:, 4:5]
        t_amb = X_inputs[:, 5:6]

        # Approximated localized conduction balance
        conduction_term = q_power / np.maximum(eff_k, 1.0)
        convection_loss_term = (2.0 * h_conv / 0.0016) * (y_pred * 60.0) * 1e-4 # Scaled dimension
        physics_residual = np.abs(conduction_term - convection_loss_term)
        l_physics = float(np.mean(physics_residual ** 2))

        # 3. Boundary Loss: Convective condition on board perimeter
        edge_dist = X_inputs[:, 6:7]
        is_edge = (edge_dist < 0.05).astype(np.float64)
        boundary_residual = is_edge * (y_pred - 0.05) # Near edge temperature approaches ambient
        l_boundary = float(np.mean(boundary_residual ** 2))

        # Total Weighted Loss
        l_total = (
            self.lambda_data * l_data
            + self.lambda_physics * l_physics
            + self.lambda_boundary * l_boundary
        )

        return PINNLossComponents(
            data_loss=round(l_data, 6),
            physics_loss=round(l_physics, 6),
            boundary_loss=round(l_boundary, 6),
            total_loss=round(l_total, 6),
        )
