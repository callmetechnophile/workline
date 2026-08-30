"""
Configuration management for EngineeringSynthesisAgent (Agent #5).
Manages Amazon Bedrock reasoning parameters, confidence defaults, and export thresholds.
"""

import os
from pydantic import BaseModel, Field


class EngineeringSynthesisConfig(BaseModel):
    """Configuration for EngineeringSynthesisAgent."""

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
        default_factory=lambda: float(os.getenv("ENGINEERING_SYNTHESIS_TEMPERATURE", "0.1"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("ENGINEERING_SYNTHESIS_MAX_TOKENS", "4096"))
    )

    # Confidence Thresholds
    min_decision_confidence: float = Field(
        default_factory=lambda: float(os.getenv("MIN_DECISION_CONFIDENCE", "0.70"))
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("ENGINEERING_SYNTHESIS_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
eng_config = EngineeringSynthesisConfig()
