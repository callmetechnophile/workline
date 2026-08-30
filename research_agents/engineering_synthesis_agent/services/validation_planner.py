"""
Validation planning and experiment design service for EngineeringSynthesisAgent (Sections 14 & 15).
"""

from typing import List, Tuple
from research_agents.engineering_synthesis_agent.schemas import (
    EngineeringDecision,
    ExperimentPlan,
    ProjectMeta,
    ValidationRequirement,
)


class ValidationPlanner:
    """Formulates verification procedures and empirical experiment designs."""

    def plan_validation(
        self,
        project: ProjectMeta,
        decisions: List[EngineeringDecision],
    ) -> Tuple[List[ValidationRequirement], List[ExperimentPlan]]:
        """
        Creates validation requirements and empirical experiment plans.
        """
        validations: List[ValidationRequirement] = []
        experiments: List[ExperimentPlan] = []
        counter = 0

        # Validation for each decision
        for dec in decisions:
            counter += 1
            validations.append(
                ValidationRequirement(
                    validation_id=f"VAL-{counter:03d}",
                    category="bench_test",
                    description=f"Bench test verification for {dec.decision_area} using selected `{dec.selected_option}`.",
                    acceptance_criteria="System operates stably within latency, power, and thermal limits under continuous full load.",
                    decision_ids=[dec.decision_id],
                )
            )

        # General power/thermal validation
        counter += 1
        validations.append(
            ValidationRequirement(
                validation_id=f"VAL-{counter:03d}",
                category="prototype_measurement",
                description="Oscilloscope measurement of DC power bus transients during GPU maximum inference bursts.",
                acceptance_criteria="Supply rail ripple < 50 mVpp, transient droop < 100 mV.",
                decision_ids=[d.decision_id for d in decisions],
            )
        )

        # Experiment Design (Section 15)
        experiments.append(
            ExperimentPlan(
                experiment_id="EXP-001",
                question="What is the minimum resolvable human temperature delta against ambient ground clutter at 25m altitude?",
                setup=[
                    "Mount thermal sensor and RGB camera to flight test gantry at 25m height.",
                    "Position heated calibration mannequin (37 deg C) on varied background surfaces (grass, asphalt, soil).",
                ],
                variables=[
                    "Ambient background temperature (15C to 35C)",
                    "Mannequin clothing insulation layers (0, 1, 2)",
                ],
                metrics=[
                    "Detection confidence score",
                    "Signal-to-Clutter Ratio (SCR)",
                    "False positive rate per frame",
                ],
                acceptance_criteria=[
                    "Detection confidence >= 0.85 with SCR >= 3.0 across all tested ground backgrounds.",
                ],
            )
        )

        return validations, experiments
