"""
Configuration, constants, sentinels, and thresholds for Agent #26 (DeploymentOpsAgent).
"""

import os
from typing import List
from pydantic import BaseModel, Field

# Zero-Fabrication Sentinel Constants
UNKNOWN: str = "UNKNOWN"
THRESHOLD_UNKNOWN: str = "THRESHOLD_UNKNOWN"
MAINTENANCE_INTERVAL_UNKNOWN: str = "MAINTENANCE_INTERVAL_UNKNOWN"
SAFETY_INFORMATION_REQUIRED: str = "SAFETY_INFORMATION_REQUIRED"
DATA_REQUIRED: str = "DATA_REQUIRED"
VALIDATED_PROCEDURE_REQUIRED: str = "VALIDATED_PROCEDURE_REQUIRED"


class DeploymentOpsConfig(BaseModel):
    """Master configuration for Agent #26."""

    agent_id: str = "Agent #26"
    agent_name: str = "DeploymentOpsAgent"
    fabric_id: str = "agent.26"
    version: str = "1.0.0"

    model_id: str = os.getenv(
        "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    # Privileged operations requiring explicit ArmorIQ authorization
    privileged_operations: List[str] = Field(
        default_factory=lambda: [
            "deploy_production",
            "service_restart",
            "firmware_update",
            "model_weight_update",
            "production_config_modify",
            "database_restore",
            "production_rollback",
            "disable_monitoring",
        ]
    )


config = DeploymentOpsConfig()
