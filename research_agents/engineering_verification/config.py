"""
Configuration settings for EngineeringVerificationAgent (Agent #18).
"""

import os
from pydantic import BaseModel, Field


class VerificationConfig(BaseModel):
    """Configuration for EngineeringVerificationAgent (Agent #18)."""

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_VERIFICATION_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("VERIFICATION_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("VERIFICATION_MAX_TOKENS", "4096"))
    )

    # Verification and Evidence Rules (Sections 2, 8, 37, 44, 77, 78)
    require_evidence_for_pass: bool = Field(default=True)
    auto_invalidate_on_change: bool = Field(default=True)
    enforce_armoriq_boundary: bool = Field(default=True)


verification_config = VerificationConfig()
