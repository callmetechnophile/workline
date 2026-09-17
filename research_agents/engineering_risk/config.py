"""
Configuration settings, rating scales, and risk matrix defaults for EngineeringRiskAgent (Agent #21).
"""

import os
from typing import Dict, List
from pydantic import BaseModel, Field


class RatingScaleConfig(BaseModel):
    """Configurable rating scale definitions (Sections 11–13)."""

    severity_scale: Dict[int, str] = Field(
        default_factory=lambda: {
            1: "Negligible - No perceptible impact on system or user",
            2: "Very Low - Minor nuisance, non-critical function slightly degraded",
            3: "Low - Minor system degradation, workarounds readily available",
            4: "Minor - Partial loss of non-essential secondary function",
            5: "Moderate - Reduced primary performance, noticeable user degradation",
            6: "Significant - Loss of primary function without safety hazard",
            7: "Major - Severe system impairment, requires manual intervention",
            8: "High - Complete system operational failure or major compliance breach",
            9: "Critical - Hazardous failure with potential safety impact or regulatory violation",
            10: "Catastrophic - Severe safety risk, total loss of containment/control",
        }
    )

    occurrence_scale: Dict[int, str] = Field(
        default_factory=lambda: {
            1: "Extremely Unlikely (< 1 in 1,000,000 operations)",
            2: "Remote (1 in 500,000 operations)",
            3: "Very Low (1 in 100,000 operations)",
            4: "Low (1 in 20,000 operations)",
            5: "Moderate-Low (1 in 5,000 operations)",
            6: "Moderate (1 in 1,000 operations)",
            7: "Moderate-High (1 in 200 operations)",
            8: "High (1 in 50 operations)",
            9: "Very High (1 in 10 operations)",
            10: "Almost Inevitable (> 1 in 2 operations)",
        }
    )

    detection_scale: Dict[int, str] = Field(
        default_factory=lambda: {
            1: "Almost Certain Detection - Automated real-time interlocking & diagnostics",
            2: "Very High - Automatic self-test with immediate fault isolation",
            3: "High - Continuous monitoring and alerting before consequence occurs",
            4: "Moderately High - Automated diagnostic check on boot/startup",
            5: "Moderate - Manual inspection / periodic automated diagnostic",
            6: "Low - Diagnostic available but requires manual trigger / test routine",
            7: "Very Low - Difficult to detect prior to operational failure",
            8: "Remote - Indirect symptoms only, difficult to pinpoint cause",
            9: "Very Remote - Unlikely to be detected before end-effect manifestation",
            10: "Undetectable - No mechanism to detect failure prior to catastrophic effect",
        }
    )


class RiskMatrixConfig(BaseModel):
    """Configurable Likelihood x Consequence Risk Matrix (Section 19–20)."""

    likelihood_levels: Dict[str, List[int]] = Field(
        default_factory=lambda: {
            "LOW": [1, 2, 3],
            "MEDIUM": [4, 5, 6],
            "HIGH": [7, 8],
            "VERY_HIGH": [9, 10],
        }
    )

    severity_levels: Dict[str, List[int]] = Field(
        default_factory=lambda: {
            "NEGLIGIBLE": [1, 2],
            "MINOR": [3, 4],
            "MODERATE": [5, 6],
            "MAJOR": [7, 8],
            "CRITICAL": [9, 10],
        }
    )

    rpn_thresholds: Dict[str, int] = Field(
        default_factory=lambda: {
            "LOW": 40,
            "MEDIUM": 100,
            "HIGH": 200,
            "CRITICAL": 300,
        }
    )


class RiskConfig(BaseModel):
    """Main configuration for EngineeringRiskAgent."""

    agent_id: str = "Agent #21"
    agent_name: str = "EngineeringRiskAgent"
    version: str = "1.0.0"

    bedrock_model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_RISK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    temperature: float = 0.0
    max_tokens: int = 4096

    # Critical risk override policy
    critical_safety_severity_threshold: int = 9
    require_human_approval_for_acceptance: bool = True
    allow_autonomous_critical_acceptance: bool = False

    rating_scales: RatingScaleConfig = Field(default_factory=RatingScaleConfig)
    risk_matrix: RiskMatrixConfig = Field(default_factory=RiskMatrixConfig)


risk_config = RiskConfig()
