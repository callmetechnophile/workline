"""
Actionable required corrections generator for EngineeringValidationAgent (Section 49).
Synthesizes prescriptive engineering remediation steps for blocking failures without altering upstream designs.
"""

from typing import List
import uuid
from research_agents.engineering_validation_agent.schemas import RequiredCorrection, ValidationItem


class CorrectionGenerator:
    """Generates prescriptive remediation guidance for blocking engineering failures."""

    def generate_corrections(self, failures: List[ValidationItem]) -> List[RequiredCorrection]:
        """
        Creates structured RequiredCorrection items for all blocking/critical failures.
        """
        corrections: List[RequiredCorrection] = []

        for fail in failures:
            if fail.status == "FAIL" or fail.blocking:
                corrections.append(
                    RequiredCorrection(
                        correction_id=f"CORR-{uuid.uuid4().hex[:6].upper()}",
                        validation_id=fail.validation_id,
                        problem=fail.title,
                        why_it_matters=fail.description,
                        recommended_correction=fail.recommended_action or "Review and correct component selection or wiring architecture.",
                        affected_components=fail.affected_components,
                        affected_subsystems=fail.affected_subsystems,
                        blocking=True,
                    )
                )

        return corrections
