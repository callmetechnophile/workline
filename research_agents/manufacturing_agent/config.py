"""
Configuration settings, process definitions, unit conversion tables, and thresholds for Agent #24.
"""

import os
from typing import Dict, List
from pydantic import BaseModel, Field


class UnitFactors(BaseModel):
    """Conversion factors to standard metric units (mm, N, MPa, etc.)."""

    length_to_mm: Dict[str, float] = Field(
        default_factory=lambda: {
            "mm": 1.0,
            "millimeter": 1.0,
            "millimeters": 1.0,
            "cm": 10.0,
            "centimeter": 10.0,
            "centimeters": 10.0,
            "m": 1000.0,
            "meter": 1000.0,
            "meters": 1000.0,
            "in": 25.4,
            "inch": 25.4,
            "inches": 25.4,
            "mil": 0.0254,
            "thou": 0.0254,
        }
    )

    force_to_newton: Dict[str, float] = Field(
        default_factory=lambda: {
            "n": 1.0,
            "newton": 1.0,
            "kn": 1000.0,
            "lbf": 4.44822,
            "kgf": 9.80665,
        }
    )

    torque_to_nm: Dict[str, float] = Field(
        default_factory=lambda: {
            "nm": 1.0,
            "n*m": 1.0,
            "n-m": 1.0,
            "in-lb": 0.112985,
            "in*lb": 0.112985,
            "ft-lb": 1.35582,
            "ft*lb": 1.35582,
        }
    )

    pressure_to_mpa: Dict[str, float] = Field(
        default_factory=lambda: {
            "mpa": 1.0,
            "kpa": 0.001,
            "pa": 0.000001,
            "bar": 0.1,
            "psi": 0.00689476,
        }
    )


class ManufacturingConfig(BaseModel):
    """Main configuration for Manufacturing / DFM-DFA Agent."""

    agent_id: str = "Agent #24"
    agent_name: str = "ManufacturingDFMAgent"
    fabric_id: str = "agent.24"
    version: str = "1.0.0"

    bedrock_model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_MANUFACTURING_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    temperature: float = 0.0
    max_tokens: int = 4096

    # Unit conversion configuration
    units: UnitFactors = Field(default_factory=UnitFactors)

    # Capability and statistical thresholds
    min_cpk_acceptable: float = 1.33
    min_cpk_preferred: float = 1.67
    min_sample_size_variation: int = 30


manufacturing_config = ManufacturingConfig()
