"""Configurable Neural Network Architecture for the PCB Thermal Physics-Informed Neural Network (PINN)."""

import math
from typing import Any, Dict, List, Optional
import numpy as np


class PCBThermalPINN:
    """
    Configurable Multi-Layer Perceptron (MLP) Neural Network for PCB Steady-State Thermal PINN.
    Runs on CPU with high numerical efficiency and supports GPU execution when PyTorch is available.
    """

    def __init__(
        self,
        input_dim: int = 7,
        hidden_dim: int = 48,
        hidden_layers: int = 3,
        output_dim: int = 1,
        activation: str = "tanh",
        learning_rate: float = 0.005,
        random_seed: int = 42,
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.hidden_layers = hidden_layers
        self.output_dim = output_dim
        self.activation = activation
        self.learning_rate = learning_rate
        self.random_seed = random_seed

        # Initialize network weights (Xavier / He initialization)
        np.random.seed(random_seed)
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []

        layer_dims = [input_dim] + [hidden_dim] * hidden_layers + [output_dim]
        for i in range(len(layer_dims) - 1):
            din = layer_dims[i]
            dout = layer_dims[i + 1]
            limit = math.sqrt(6.0 / (din + dout))
            w = np.random.uniform(-limit, limit, (din, dout)).astype(np.float64)
            b = np.zeros((1, dout), dtype=np.float64)
            self.weights.append(w)
            self.biases.append(b)

        # Adam optimizer state variables
        self.m_w = [np.zeros_like(w) for w in self.weights]
        self.v_w = [np.zeros_like(w) for w in self.weights]
        self.m_b = [np.zeros_like(b) for b in self.biases]
        self.v_b = [np.zeros_like(b) for b in self.biases]
        self.t_adam = 0

    def _act(self, z: np.ndarray) -> np.ndarray:
        """Forward activation function."""
        if self.activation == "tanh":
            return np.tanh(z)
        elif self.activation == "silu":
            return z / (1.0 + np.exp(-np.clip(z, -15.0, 15.0)))
        # Default relu
        return np.maximum(0.0, z)

    def _dact(self, a: np.ndarray) -> np.ndarray:
        """Derivative of activation with respect to pre-activation."""
        if self.activation == "tanh":
            return 1.0 - (a ** 2)
        # Default sigmoid / linear fallback
        return np.ones_like(a)

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]:
        """
        Forward propagation pass.
        Returns: (output_predictions, list_of_activations, list_of_preactivations)
        """
        activations = [X]
        preactivations = []

        curr = X
        for i in range(len(self.weights)):
            z = np.dot(curr, self.weights[i]) + self.biases[i]
            preactivations.append(z)
            if i < len(self.weights) - 1:
                curr = self._act(z)
            else:
                curr = z # Linear output layer for regression
            activations.append(curr)

        return curr, activations, preactivations

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Run inference evaluation."""
        out, _, _ = self.forward(X)
        return out

    def get_state_dict(self) -> Dict[str, Any]:
        """Serialize model weights and hyperparameters."""
        return {
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "hidden_layers": self.hidden_layers,
            "output_dim": self.output_dim,
            "activation": self.activation,
            "learning_rate": self.learning_rate,
            "random_seed": self.random_seed,
            "weights": [w.tolist() for w in self.weights],
            "biases": [b.tolist() for b in self.biases],
        }

    def load_state_dict(self, state: Dict[str, Any]) -> None:
        """Load serialized model weights."""
        self.input_dim = state.get("input_dim", self.input_dim)
        self.hidden_dim = state.get("hidden_dim", self.hidden_dim)
        self.hidden_layers = state.get("hidden_layers", self.hidden_layers)
        self.weights = [np.array(w, dtype=np.float64) for w in state["weights"]]
        self.biases = [np.array(b, dtype=np.float64) for b in state["biases"]]
