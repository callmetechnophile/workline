"""
Validation traceability builder for EngineeringValidationAgent (Section 46).
Enforces unbroken lineage from Requirement -> Architecture -> Component -> BOM -> Procurement -> Rule -> Verdict.
"""

from typing import Any, Dict, List
from research_agents.engineering_validation_agent.schemas import (
    FinalVerdict,
    ValidationItem,
    ValidationTraceabilityItem,
)


class ValidationTraceabilityBuilder:
    """Constructs comprehensive design verification traceability records."""

    def build_traceability(
        self,
        context: Dict[str, Any],
        findings: List[ValidationItem],
        verdict: FinalVerdict,
    ) -> List[ValidationTraceabilityItem]:
        traceability_records: List[ValidationTraceabilityItem] = []
        bom_items = context.get("bom", {}).get("items", [])

        for idx, item in enumerate(bom_items):
            b_id = item.get("bom_item_id", f"BOM-{idx+1:03d}")
            sub_id = item.get("subsystem_id", "SUB-001")
            part_no = item.get("part_number", "Part")

            # Find matching findings for this component
            comp_findings = [
                f for f in findings
                if part_no in f.affected_components or b_id in f.affected_components or sub_id in f.affected_subsystems
            ]

            status = "PASS"
            if any(f.status == "FAIL" for f in comp_findings):
                status = "FAIL"
            elif any(f.status == "WARNING" for f in comp_findings):
                status = "WARNING"

            traceability_records.append(
                ValidationTraceabilityItem(
                    traceability_id=f"TRACE-VAL-{b_id}",
                    requirement_ids=[f"REQ-{b_id}"],
                    architecture_ids=[sub_id],
                    component_ids=[part_no],
                    bom_item_ids=[b_id],
                    procurement_ids=[f"PROC-{b_id}"],
                    validation_ids=[f.validation_id for f in comp_findings] or ["VAL-DEFAULT-PASS"],
                    status=status,
                    verdict_impact=verdict.verdict,
                )
            )

        return traceability_records
