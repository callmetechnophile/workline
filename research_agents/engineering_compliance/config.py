"""
Configuration settings for EngineeringComplianceAgent (Agent #17).
"""

import os
from pydantic import BaseModel, Field


class ComplianceConfig(BaseModel):
    """Configuration for EngineeringComplianceAgent (Agent #17)."""

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_COMPLIANCE_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("COMPLIANCE_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("COMPLIANCE_MAX_TOKENS", "4096"))
    )

    # Gate & Safeguard Rules (Sections 2, 3, 38, 41, 42)
    allow_unknown_as_pass: bool = Field(default=False)
    block_on_critical_failure: bool = Field(default=True)
    require_evidence_linkage: bool = Field(default=True)


compliance_config = ComplianceConfig()
