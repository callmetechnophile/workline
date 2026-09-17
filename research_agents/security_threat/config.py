"""
Configuration settings, risk scales, security gates, and thresholds for SecurityThreatModelingAgent (Agent #22).
"""

import os
from typing import Dict, List
from pydantic import BaseModel, Field


class SecurityScaleConfig(BaseModel):
    """Configurable likelihood and impact scales for security risk scoring."""

    likelihood_scale: Dict[int, str] = Field(
        default_factory=lambda: {
            1: "Very Low - Requires extraordinary attacker capability, zero-day exploit chain, and direct physical access",
            2: "Low - High attack complexity, authenticated insider with niche access required",
            3: "Moderate - Standard web/API attacker capability, public network access",
            4: "High - Low complexity, script kiddie / automated scanner can discover and trigger",
            5: "Critical - Trivial, unauthenticated remote trigger with public exploit available",
        }
    )

    impact_scale: Dict[int, str] = Field(
        default_factory=lambda: {
            1: "Negligible - Informational leakage without operational or security consequence",
            2: "Minor - Minor non-sensitive data exposure or localized temporary rate-limiting",
            3: "Moderate - Partial data modification, elevation to standard user role",
            4: "Major - Sensitive project data exfiltration, unauthorized tool invocation",
            5: "Catastrophic - Full tenant isolation bypass, arbitrary remote code execution, database compromise, credential theft",
        }
    )

    risk_thresholds: Dict[str, int] = Field(
        default_factory=lambda: {
            "LOW": 4,
            "MEDIUM": 9,
            "HIGH": 16,
            "CRITICAL": 20,
        }
    )


class SecurityConfig(BaseModel):
    """Main configuration for SecurityThreatModelingAgent."""

    agent_id: str = "Agent #22"
    agent_name: str = "SecurityThreatModelingAgent"
    version: str = "1.0.0"

    bedrock_model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_SECURITY_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    temperature: float = 0.0
    max_tokens: int = 4096

    # Security policy enforcement
    require_human_for_critical_acceptance: bool = True
    allow_autonomous_critical_acceptance: bool = False
    critical_risk_threshold: int = 20

    scales: SecurityScaleConfig = Field(default_factory=SecurityScaleConfig)


security_config = SecurityConfig()
