"""
Configuration settings for EngineeringOptimizationAgent (Agent #20).
"""

import os
from pydantic import BaseModel, Field


class OptimizationConfig(BaseModel):
    """Configuration for EngineeringOptimizationAgent (Agent #20)."""

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_OPTIMIZATION_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("OPTIMIZATION_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("OPTIMIZATION_MAX_TOKENS", "4096"))
    )

    # Optimization engine policies
    max_candidates: int = Field(default=50)
    default_random_seed: int = Field(default=42)
    max_sweep_points: int = Field(default=200)
    hard_constraint_tolerance: float = Field(default=0.0)  # Zero tolerance for hard constraints
    pareto_epsilon: float = Field(default=1e-9)  # Floating-point epsilon for dominance checks


optimization_config = OptimizationConfig()
