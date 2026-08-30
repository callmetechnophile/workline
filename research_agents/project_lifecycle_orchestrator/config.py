"""
Configuration settings for ProjectLifecycleOrchestrator (Agent #14).
"""

import os
from pydantic import BaseModel, Field


class OrchestratorConfig(BaseModel):
    """Configuration for ProjectLifecycleOrchestrator (Agent #14)."""

    # Safety and loop prevention limits (Sections 41, 42, 44)
    max_actions_per_cycle: int = Field(
        default_factory=lambda: int(os.getenv("ORCHESTRATOR_MAX_ACTIONS", "10"))
    )
    max_retries: int = Field(
        default_factory=lambda: int(os.getenv("ORCHESTRATOR_MAX_RETRIES", "3"))
    )
    max_delegation_depth: int = Field(
        default_factory=lambda: int(os.getenv("ORCHESTRATOR_MAX_DEPTH", "5"))
    )
    max_parallel_tasks: int = Field(
        default_factory=lambda: int(os.getenv("ORCHESTRATOR_MAX_PARALLEL", "4"))
    )
    max_execution_time_sec: int = Field(
        default_factory=lambda: int(os.getenv("ORCHESTRATOR_MAX_TIME_SEC", "300"))
    )
    auto_pause_on_human: bool = Field(
        default_factory=lambda: os.getenv("ORCHESTRATOR_PAUSE_ON_HUMAN", "true").lower() == "true"
    )

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_ORCHESTRATOR_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("ORCHESTRATOR_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("ORCHESTRATOR_MAX_TOKENS", "4096"))
    )


orchestrator_config = OrchestratorConfig()
