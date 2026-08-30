"""
Configuration settings for EngineeringCopilotAgent (Agent #15).
"""

import os
from pydantic import BaseModel, Field


class CopilotConfig(BaseModel):
    """Configuration for EngineeringCopilotAgent (Agent #15)."""

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_COPILOT_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("COPILOT_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("COPILOT_MAX_TOKENS", "4096"))
    )

    # Graph Traversal Limits (Section 45)
    max_traversal_depth: int = Field(
        default_factory=lambda: int(os.getenv("COPILOT_MAX_DEPTH", "10"))
    )
    max_nodes_per_query: int = Field(
        default_factory=lambda: int(os.getenv("COPILOT_MAX_NODES", "500"))
    )
    require_evidence_grounding: bool = Field(
        default_factory=lambda: os.getenv("COPILOT_REQUIRE_EVIDENCE", "true").lower() == "true"
    )


copilot_config = CopilotConfig()
