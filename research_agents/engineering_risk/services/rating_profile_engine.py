"""
Configurable Rating Scale and Risk Matrix Evaluation Engine (Agent #21).
"""

from typing import Dict, List, Optional
from research_agents.engineering_risk.config import risk_config
from research_agents.engineering_risk.schemas import (
    RatingProfile,
    RiskLevelLiteral,
    RiskMatrixProfile,
)


class RatingProfileEngine:
    """Evaluates configurable rating scales and 2D Likelihood x Consequence matrices."""

    def get_default_rating_profile(self) -> RatingProfile:
        return RatingProfile(
            name="WorkflowGuide AI Standard Engineering Rating Profile",
            severity_scale=risk_config.rating_scales.severity_scale,
            occurrence_scale=risk_config.rating_scales.occurrence_scale,
            detection_scale=risk_config.rating_scales.detection_scale,
            risk_thresholds=risk_config.risk_matrix.rpn_thresholds,
            source="IEC 60812 / ISO 26262 Standards Adaptation",
            version="1.0.0",
        )

    def get_default_risk_matrix(self) -> RiskMatrixProfile:
        return RiskMatrixProfile(
            likelihood_levels=risk_config.risk_matrix.likelihood_levels,
            severity_levels=risk_config.risk_matrix.severity_levels,
            risk_bands={
                "LOW_NEGLIGIBLE": "LOW",
                "LOW_MINOR": "LOW",
                "LOW_MODERATE": "MEDIUM",
                "LOW_MAJOR": "HIGH",
                "LOW_CRITICAL": "CRITICAL",
                "MEDIUM_NEGLIGIBLE": "LOW",
                "MEDIUM_MINOR": "MEDIUM",
                "MEDIUM_MODERATE": "MEDIUM",
                "MEDIUM_MAJOR": "HIGH",
                "MEDIUM_CRITICAL": "CRITICAL",
                "HIGH_NEGLIGIBLE": "MEDIUM",
                "HIGH_MINOR": "HIGH",
                "HIGH_MODERATE": "HIGH",
                "HIGH_MAJOR": "CRITICAL",
                "HIGH_CRITICAL": "CRITICAL",
                "VERY_HIGH_NEGLIGIBLE": "HIGH",
                "VERY_HIGH_MINOR": "HIGH",
                "VERY_HIGH_MODERATE": "CRITICAL",
                "VERY_HIGH_MAJOR": "CRITICAL",
                "VERY_HIGH_CRITICAL": "CRITICAL",
            },
            source="MIL-STD-882E Risk Assessment Matrix",
            version="1.0.0",
        )

    def classify_matrix(
        self,
        likelihood_score: int,
        severity_score: int,
        matrix: Optional[RiskMatrixProfile] = None,
    ) -> RiskLevelLiteral:
        """Classify (Likelihood, Severity) into LOW, MEDIUM, HIGH, CRITICAL."""
        if severity_score >= risk_config.critical_safety_severity_threshold:
            return "CRITICAL"

        # Determine likelihood band
        l_band = "LOW"
        if likelihood_score >= 9:
            l_band = "VERY_HIGH"
        elif likelihood_score >= 7:
            l_band = "HIGH"
        elif likelihood_score >= 4:
            l_band = "MEDIUM"

        # Determine severity band
        s_band = "NEGLIGIBLE"
        if severity_score >= 9:
            s_band = "CRITICAL"
        elif severity_score >= 7:
            s_band = "MAJOR"
        elif severity_score >= 5:
            s_band = "MODERATE"
        elif severity_score >= 3:
            s_band = "MINOR"

        mat = matrix or self.get_default_risk_matrix()
        key = f"{l_band}_{s_band}"
        return mat.risk_bands.get(key, "MEDIUM")
