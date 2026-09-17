"""
Tolerance and GD&T Manufacturability & 1D Stack-Up Engine (Section 4).
"""

import math
from typing import Any, Dict, List, Optional, Tuple
from research_agents.manufacturing_agent.schemas import ToleranceItem
from research_agents.manufacturing_agent.services.unit_normalizer import UnitNormalizer


class ToleranceEngine:
    """Classifies tolerances, detects over-specification, and calculates 1D tolerance stack-ups."""

    def __init__(self):
        self.normalizer = UnitNormalizer()

    def evaluate_tolerance(
        self,
        item: Dict[str, Any],
    ) -> ToleranceItem:
        cid = item.get("component_id", "COMP-001")
        feature = item.get("feature_name", "Linear Dimension")
        nom = float(item.get("nominal_value", 10.0))
        unit = item.get("unit", "mm")
        upper = float(item.get("upper_tol", 0.05))
        lower = float(item.get("lower_tol", -0.05))

        span = abs(upper - lower)
        norm_span, err = self.normalizer.normalize_length(span, unit)

        classification = "FUNCTIONALLY_REQUIRED"
        if norm_span is not None:
            if norm_span < 0.01:
                classification = "MANUFACTURING_CONCERN"
            elif norm_span > 0.5:
                classification = "LIKELY_OVER_SPECIFIED"
        else:
            classification = "UNRESOLVED"

        return ToleranceItem(
            tolerance_id=item.get("tolerance_id", f"TOL-{cid}"),
            component_id=cid,
            feature_name=feature,
            datum=item.get("datum"),
            nominal_value=nom,
            unit=unit,
            upper_tol=upper,
            lower_tol=lower,
            normalized_span_mm=norm_span,
            classification=classification,
            inspection_method=item.get("inspection_method", "CMM / Micrometer"),
            notes=item.get("notes", ""),
        )

    def calculate_1d_stackup(
        self,
        tolerances: List[ToleranceItem],
    ) -> Dict[str, Any]:
        """Calculates linear 1D Worst-Case (WC) and Root-Sum-Square (RSS) tolerance stack-up."""
        total_nominal = 0.0
        wc_upper = 0.0
        wc_lower = 0.0
        rss_variance = 0.0

        for t in tolerances:
            norm_nom, _ = self.normalizer.normalize_length(t.nominal_value, t.unit)
            norm_upper, _ = self.normalizer.normalize_length(t.upper_tol, t.unit)
            norm_lower, _ = self.normalizer.normalize_length(t.lower_tol, t.unit)

            if norm_nom is None or norm_upper is None or norm_lower is None:
                return {
                    "status": "ERROR",
                    "error": "UNIT_AMBIGUOUS: Stack-up calculation blocked due to ambiguous units.",
                }

            total_nominal += norm_nom
            wc_upper += norm_upper
            wc_lower += norm_lower
            half_tol = (norm_upper - norm_lower) / 2.0
            rss_variance += half_tol ** 2

        rss_tol = math.sqrt(rss_variance)
        return {
            "status": "SUCCESS",
            "total_nominal_mm": round(total_nominal, 4),
            "worst_case_upper_mm": round(wc_upper, 4),
            "worst_case_lower_mm": round(wc_lower, 4),
            "worst_case_span_mm": round(wc_upper - wc_lower, 4),
            "rss_tolerance_mm": round(rss_tol, 4),
            "rss_max_mm": round(total_nominal + rss_tol, 4),
            "rss_min_mm": round(total_nominal - rss_tol, 4),
        }
