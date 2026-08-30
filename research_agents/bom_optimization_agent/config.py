"""
Configuration management for BOMOptimizationAgent (Agent #8).
Manages Amazon Bedrock reasoning parameters, default destination, currency, and optimization thresholds.
"""

import os
from pydantic import BaseModel, Field


class BOMOptimizationConfig(BaseModel):
    """Configuration for BOMOptimizationAgent."""

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
        default_factory=lambda: float(os.getenv("BOM_OPTIMIZATION_TEMPERATURE", "0.1"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("BOM_OPTIMIZATION_MAX_TOKENS", "4096"))
    )

    # Logistics Defaults
    default_destination_city: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_DESTINATION_CITY", "Bengaluru")
    )
    default_destination_state: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_DESTINATION_STATE", "Karnataka")
    )
    default_destination_country: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_DESTINATION_COUNTRY", "India")
    )
    default_destination_postal_code: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_DESTINATION_POSTAL_CODE", "560001")
    )
    default_currency: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_CURRENCY", "INR")
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("BOM_OPTIMIZATION_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
opt_config = BOMOptimizationConfig()
