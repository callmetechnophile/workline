"""
Configuration management for EngineeringArchitectureAgent (Agent #6).
Manages Amazon Bedrock reasoning parameters, confidence defaults, and export thresholds.
"""

import os
from pydantic import BaseModel, Field


class EngineeringArchitectureConfig(BaseModel):
    """Configuration for EngineeringArchitectureAgent."""

    # Amazon Bedrock Settings
    bedrock_model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
        )
    )
    bedrock_region: str = Field(
        default_factory=lambda: os.getenv("BEDROCK_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("ENGINEERING_ARCHITECTURE_TEMPERATURE", "0.1"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("ENGINEERING_ARCHITECTURE_MAX_TOKENS", "4096"))
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("ENGINEERING_ARCHITECTURE_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
arch_config = EngineeringArchitectureConfig()
