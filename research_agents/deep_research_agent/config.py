"""
Configuration management for DeepResearchAgent (Agent #4).
Reads Amazon Bedrock model IDs, AWS region, temperature, and token budgets from environment.
"""

import os
from pydantic import BaseModel, Field


class DeepResearchConfig(BaseModel):
    """Configuration for DeepResearchAgent and Amazon Bedrock reasoning provider."""

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
        default_factory=lambda: float(os.getenv("BEDROCK_TEMPERATURE", "0.2"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("BEDROCK_TIMEOUT_SECONDS", "60.0"))
    )

    # Synthesis Limits
    max_evidence_items: int = Field(
        default_factory=lambda: int(os.getenv("DEEP_RESEARCH_MAX_EVIDENCE", "50"))
    )

    # Logging
    log_level: str = Field(
        default_factory=lambda: os.getenv("DEEP_RESEARCH_LOG_LEVEL", "INFO")
    )


# Singleton configuration instance
deep_research_config = DeepResearchConfig()
