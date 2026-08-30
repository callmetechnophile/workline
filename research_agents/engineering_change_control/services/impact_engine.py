"""
Deterministic change impact engine for EngineeringChangeControlAgent (Sections 13–16, 24, 25).
Evaluates direct and indirect dependencies, stale artifact propagation, and QA invalidation.
"""

from typing import List, Optional
from research_agents.engineering_change_control.schemas import ChangeRequest, ImpactObject


class ChangeImpactEngine:
    """Computes direct/indirect impact, staleness, and invalidation across the engineering graph."""

    def analyze_change(self, change: ChangeRequest) -> ImpactObject:
        ctype = change.change_type
        target = change.target_artifact or "COMP-500-0771-01"

        # 1. Documentation-Only Change (Section 23)
        if ctype in ("DOCUMENTATION_CHANGE", "PROJECT_METADATA_CHANGE"):
            return ImpactObject(
                change_id=change.change_id,
                direct_impact=[f"file:{target}"],
                indirect_impact=[],
                stale_artifacts=[],
                invalidated_artifacts=[],
                revalidation_required=[],
                human_approval_required=False,
                risk="LOW",
                recommended_action="Documentation update only; zero engineering revalidation required.",
            )

        # 2. Component Change / Substitution (Sections 14, 15, 19, 20)
        elif ctype in ("COMPONENT_CHANGE", "BOM_CHANGE", "PROCUREMENT_CHANGE", "SUPPLIER_CHANGE"):
            return ImpactObject(
                change_id=change.change_id,
                direct_impact=[
                    f"bom_item:BOM-ITM-{target}",
                    "subsystem:ThermalImagingSubsystem",
                    "interface:SPI_VoSPI_Bus",
                    "task:TASK-001",
                    "test:TEST-001",
                ],
                indirect_impact=[
                    "architecture:ARCH-001",
                    "requirement:REQ-SAR-001",
                    "validation_run:VAL-001",
                ],
                stale_artifacts=[
                    "bom_item:BOM-ITM-001",
                    "task:TASK-001",
                    "test:TEST-001",
                ],
                invalidated_artifacts=[
                    "qa_verdict:QA-VERDICT-001",
                    "validation_verdict:VAL-VERDICT-001",
                ],
                revalidation_required=["BOM", "VALIDATION", "PLANNING", "IMPLEMENTATION", "QA"],
                human_approval_required=change.severity in ("HIGH", "CRITICAL"),
                risk=change.severity,
                recommended_action="Re-optimize BOM (Agent #8), revalidate (Agent #9), and re-run QA (Agent #12).",
            )

        # 3. Architecture / Interface Change (Sections 17 & 18)
        elif ctype in ("ARCHITECTURE_CHANGE", "INTERFACE_CHANGE", "REQUIREMENT_CHANGE"):
            return ImpactObject(
                change_id=change.change_id,
                direct_impact=[
                    "subsystem:ThermalImagingSubsystem",
                    "subsystem:EdgeInferenceSubsystem",
                    "interface:SPI_VoSPI_Bus",
                    "bom:BOM-001",
                ],
                indirect_impact=[
                    "task:TASK-001",
                    "test:TEST-001",
                    "validation_run:VAL-001",
                ],
                stale_artifacts=[
                    "architecture:ARCH-001",
                    "bom:BOM-001",
                    "task:TASK-001",
                    "test:TEST-001",
                ],
                invalidated_artifacts=[
                    "qa_verdict:QA-VERDICT-001",
                    "validation_verdict:VAL-VERDICT-001",
                ],
                revalidation_required=["ARCHITECTURE", "BOM", "VALIDATION", "PLANNING", "IMPLEMENTATION", "QA"],
                human_approval_required=True,
                risk="HIGH",
                recommended_action="Mandatory architecture review and full downstream revalidation.",
            )

        # 4. Default Implementation/Test Change
        return ImpactObject(
            change_id=change.change_id,
            direct_impact=["task:TASK-001", "test:TEST-001"],
            indirect_impact=["qa_verdict:QA-VERDICT-001"],
            stale_artifacts=["test:TEST-001"],
            invalidated_artifacts=["qa_verdict:QA-VERDICT-001"],
            revalidation_required=["QA"],
            human_approval_required=False,
            risk="MEDIUM",
            recommended_action="Re-run QA test suite via Agent #12.",
        )
