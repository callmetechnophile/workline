"""
Configuration settings for EngineeringSimulationAgent (Agent #19).
"""

import os
from pydantic import BaseModel, Field


class SimulationConfig(BaseModel):
    """Configuration for EngineeringSimulationAgent (Agent #19)."""

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_SIMULATION_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("SIMULATION_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("SIMULATION_MAX_TOKENS", "4096"))
    )

    # Simulation and Execution Policies (Sections 16, 25, 26, 78)
    default_timeout_seconds: float = Field(default=30.0)
    enforce_unit_consistency: bool = Field(default=True)
    default_random_seed: int = Field(default=42)
    max_monte_carlo_samples: int = Field(default=1000)


simulation_config = SimulationConfig()
