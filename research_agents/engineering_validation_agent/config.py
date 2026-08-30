"""
Configuration management for EngineeringValidationAgent (Agent #9).
Manages Amazon Bedrock reasoning parameters and validation thresholds.
"""

import os
from pydantic import BaseModel, Field


class EngineeringValidationConfig(BaseModel):
    """Configuration for EngineeringValidationAgent."""

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
        default_factory=lambda: float(os.getenv("VALIDATION_TEMPERATURE", "0.1"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("VALIDATION_MAX_TOKENS", "4096"))
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("VALIDATION_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
val_config = EngineeringValidationConfig()
