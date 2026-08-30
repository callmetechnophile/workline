"""
Configuration settings for EngineeringExecutionAgent (Agent #11).
"""

import os
from pydantic import BaseModel, Field


class ExecutionConfig(BaseModel):
    """Configuration for Agent #11 Execution Agent."""

    # Bedrock reasoning configuration
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_EXECUTION_MODEL_ID",
            "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("EXECUTION_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("EXECUTION_MAX_TOKENS", "4096"))
    )

    # Security & Execution limits
    default_timeout_sec: int = Field(
        default_factory=lambda: int(os.getenv("EXECUTION_TIMEOUT_SEC", "300"))
    )
    max_task_retries: int = Field(
        default_factory=lambda: int(os.getenv("MAX_TASK_RETRIES", "1"))
    )
    allow_git_push_default: bool = False
    allow_git_commit_default: bool = False
    dry_run_default: bool = False

    # ArmorIQ configuration
    armoriq_enabled: bool = Field(
        default_factory=lambda: os.getenv("DISABLE_ARMORIQ", "false").lower() != "true"
    )
    armoriq_secret_salt: str = Field(
        default_factory=lambda: os.getenv("ARMORIQ_SECRET_SALT", "armoriq-cryptographic-secure-salt-2026")
    )


exec_config = ExecutionConfig()
