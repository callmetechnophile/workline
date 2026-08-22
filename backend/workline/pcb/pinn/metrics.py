"""PINN Validation Error Metrics comparing predictions against numerical reference solver."""

import math
from typing import Dict
import numpy as np
from pydantic import BaseModel


class PINNValidationMetrics(BaseModel):
    """
    Quantitative accuracy metrics evaluated strictly on test/validation data.
    Never claimed as 'physics accurate' unless supported by measured reference errors.
    """
    mae_celsius: float                 # Mean Absolute Error in °C
    rmse_celsius: float                # Root Mean Squared Error in °C
    max_absolute_error_celsius: float  # Peak discrepancy at any board point in °C
    relative_l2_error_pct: float       # Percentage relative error (%)
    sample_count: int


class PINNMetricsCalculator:
    """Calculates statistical and physical discrepancy metrics."""

    @staticmethod
    def evaluate(y_pred_celsius: np.ndarray, y_true_celsius: np.ndarray) -> PINNValidationMetrics:
        """Computes MAE, RMSE, Maximum Error, and Relative Error."""
        diff = np.abs(y_pred_celsius.flatten() - y_true_celsius.flatten())

        mae = float(np.mean(diff))
        rmse = float(math.sqrt(np.mean(diff ** 2)))
        max_err = float(np.max(diff))

        norm_ref = float(np.linalg.norm(y_true_celsius.flatten()))
        norm_diff = float(np.linalg.norm(diff))
        rel_l2 = float((norm_diff / max(norm_ref, 1e-4)) * 100.0)

        return PINNValidationMetrics(
            mae_celsius=round(mae, 3),
            rmse_celsius=round(rmse, 3),
            max_absolute_error_celsius=round(max_err, 3),
            relative_l2_error_pct=round(rel_l2, 2),
            sample_count=len(diff),
        )
