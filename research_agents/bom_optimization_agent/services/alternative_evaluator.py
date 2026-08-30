"""
Alternative component economic evaluation service for BOMOptimizationAgent (Sections 10 & 18).
"""

from typing import Any, Dict, List


class AlternativeEvaluator:
    """Evaluates cost trade-offs and engineering approval requirements for alternative parts."""

    def evaluate_alternatives(
        self,
        component_alternatives: List[Dict[str, Any]],
        bom_items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Evaluates potential cost savings and engineering risks across alternative components.
        """
        evaluated: List[Dict[str, Any]] = []

        for alt in component_alternatives:
            compat = str(alt.get("compatibility", "")).lower()
            requires_approval = compat not in (
                "drop_in",
                "electrically_compatible",
                "functionally_equivalent",
            )

            evaluated.append(
                {
                    "alternative_id": alt.get("alternative_id", "ALT-001"),
                    "part_number": alt.get("part_number", "Unknown"),
                    "manufacturer": alt.get("manufacturer", "Unknown"),
                    "compatibility": compat,
                    "requires_engineering_approval": requires_approval,
                    "reason": alt.get("reason", "Alternative component option."),
                    "datasheet_url": alt.get("datasheet_url"),
                }
            )

        return evaluated
