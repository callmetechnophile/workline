"""
Configuration settings for EngineeringChangeControlAgent (Agent #16).
"""

import os
from pydantic import BaseModel, Field


class ChangeControlConfig(BaseModel):
    """Configuration for EngineeringChangeControlAgent (Agent #16)."""

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_CHANGE_CONTROL_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("CHANGE_CONTROL_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("CHANGE_CONTROL_MAX_TOKENS", "4096"))
    )

    # Change Policy Safeguards (Sections 30–33, 77)
    require_independent_approval_for_critical: bool = Field(
        default_factory=lambda: os.getenv("REQUIRE_INDEPENDENT_APPROVAL", "true").lower() == "true"
    )
    auto_invalidate_dependent_qa: bool = Field(
        default_factory=lambda: os.getenv("AUTO_INVALIDATE_DEPENDENT_QA", "true").lower() == "true"
    )
    preserve_full_version_history: bool = Field(
        default_factory=lambda: os.getenv("PRESERVE_FULL_VERSION_HISTORY", "true").lower() == "true"
    )


change_control_config = ChangeControlConfig()
