"""
Engineering risk evaluation for change requests (Sections 28 & 29).
"""

from typing import List
from research_agents.engineering_change_control.schemas import ChangeRequest, RiskObject


class ChangeRiskAnalyzer:
    """Evaluates safety, interface, thermal, and functional risk dimensions."""

    def evaluate_risks(self, change: ChangeRequest) -> List[RiskObject]:
        risks: List[RiskObject] = []
        ctype = change.change_type

        if ctype in ("ARCHITECTURE_CHANGE", "INTERFACE_CHANGE"):
            risks.append(
                RiskObject(
                    change_id=change.change_id,
                    category="interface_compatibility",
                    severity="HIGH",
                    description="Interface modification may cause timing or pinout incompatibilities on the hardware bus.",
                    affected_artifacts=[change.target_artifact or "interface:SPI_VoSPI_Bus"],
                    mitigation="Mandate Agent #9 validation gate and SPI signal timing verification.",
                )
            )

        if ctype in ("COMPONENT_CHANGE", "BOM_CHANGE"):
            risks.append(
                RiskObject(
                    change_id=change.change_id,
                    category="functional_equivalence",
                    severity=change.severity,
                    description="Component substitution requires verification of electrical and thermal operating constraints.",
                    affected_artifacts=[change.target_artifact or "component:500-0771-01"],
                    mitigation="Validate voltage drop, quiescent current, and sensor resolution against REQ-SAR-001.",
                )
            )

        if not risks:
            risks.append(
                RiskObject(
                    change_id=change.change_id,
                    category="general_metadata",
                    severity="LOW",
                    description="Non-functional change with zero hardware risk.",
                    affected_artifacts=[change.target_artifact or "file:README.md"],
                    mitigation="Review text diff prior to version commit.",
                )
            )

        return risks
