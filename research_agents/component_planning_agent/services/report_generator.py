"""
Publication-ready Markdown Bill of Materials report generator for ComponentPlanningAgent (Section 47).
Groups BOM line items by subsystem domain and renders comprehensive technical summaries.
"""

from typing import Any, Dict, List
from research_agents.component_planning_agent.schemas import (
    BOMAssumptionItem,
    BOMItem,
    BOMSummary,
    BOMTraceabilityItem,
    BOMUnknownItem,
    BOMValidationItem,
    CompatibilityCheck,
    ComponentAlternativeItem,
    ComponentRequirementItem,
    ProjectMeta,
    ResourceConflict,
)


class BOMReportGenerator:
    """Renders comprehensive Markdown engineering Bill of Materials."""

    def generate_report(
        self,
        project: ProjectMeta,
        bom_id: str,
        summary: BOMSummary,
        items: List[BOMItem],
        component_requirements: List[ComponentRequirementItem],
        conflicts: List[ResourceConflict],
        compatibility_checks: List[CompatibilityCheck],
        alternatives: List[ComponentAlternativeItem],
        validations: List[BOMValidationItem],
        unknowns: List[BOMUnknownItem],
        assumptions: List[BOMAssumptionItem],
        traceability: List[BOMTraceabilityItem],
    ) -> str:
        """Assembles all subsystem domains into a structured Markdown document."""
        lines: List[str] = []

        # Title
        lines.append(f"# Engineering Bill of Materials: {project.title}\n")
        lines.append(f"**BOM ID:** `{bom_id}`  ")
        if project.engineering_domain:
            lines.append(f"**Engineering Domain:** {project.engineering_domain}  ")
        lines.append(f"**Total Line Items:** `{summary.total_line_items}` | **Selected:** `{summary.selected_items}` | **Pending:** `{summary.pending_items}`\n")

        # 1. BOM Summary
        lines.append("## 1. BOM Summary\n")
        lines.append("| Metric | Count |")
        lines.append("|---|---|")
        lines.append(f"| Total Line Items | `{summary.total_line_items}` |")
        lines.append(f"| Selected Components | `{summary.selected_items}` |")
        lines.append(f"| Candidate Components | `{summary.candidate_items}` |")
        lines.append(f"| Pending Selection | `{summary.pending_items}` |")
        lines.append(f"| Subsystems Covered | `{summary.subsystem_count}` |")
        lines.append("")

        # 2. System Architecture Mapping
        lines.append("## 2. System Architecture Mapping\n")
        lines.append("| Line # | Component Name | Manufacturer | Part Number | Subsystem | Category | Status |")
        lines.append("|---|---|---|---|---|---|---|")
        for item in items:
            lines.append(f"| {item.line_number} | **{item.component_name}** | {item.manufacturer} | `{item.part_number}` | `{item.subsystem_id}` | `{item.category}` | `{item.selection_status.upper()}` |")
        lines.append("")

        # Subsystem Groupings (Compute, Sensors, Power, Control, Passives)
        subsystem_groups = {
            "Compute Components": [i for i in items if i.category in ("SBC", "microprocessor", "GPU", "AI accelerator")],
            "Sensor Components": [i for i in items if i.category in ("sensor", "camera", "thermal camera")],
            "Control Components": [i for i in items if i.category in ("microcontroller", "relay", "MOSFET")],
            "Power Components": [i for i in items if i.category in ("DC-DC converter", "voltage regulator", "LDO", "battery", "BMS")],
            "Passives & Protection": [i for i in items if i.category in ("capacitor", "resistor", "inductor", "fuse", "diode", "TVS")],
        }

        sec_num = 3
        for group_name, group_items in subsystem_groups.items():
            lines.append(f"## {sec_num}. {group_name}\n")
            sec_num += 1
            if not group_items:
                lines.append("*No dedicated components allocated in this category.*\n")
                continue

            for it in group_items:
                lines.append(f"### `{it.bom_item_id}` — {it.component_name} ({it.manufacturer} `{it.part_number}`)\n")
                lines.append(f"- **Role:** `{it.role}` ({it.subsystem_id})")
                lines.append(f"- **Quantity:** `{it.quantity} {it.unit}` | **Status:** `{it.selection_status.upper()}` | **Confidence:** `{it.confidence * 100:.0f}%`")
                lines.append(f"- **Selection Rationale:** {it.selection_reason}")
                if it.datasheet_url:
                    lines.append(f"- **Datasheet:** [View Technical Datasheet]({it.datasheet_url})")

                if it.required_specifications:
                    lines.append("- **Required Specifications:** " + ", ".join(f"`{k}: {v}`" for k, v in it.required_specifications.items()))
                if it.known_specifications:
                    lines.append("- **Known Specifications:** " + ", ".join(f"`{k}: {v}`" for k, v in it.known_specifications.items()))
                if it.interfaces:
                    lines.append(f"- **Interfaces:** {', '.join(it.interfaces)}")
                if it.software_requirements:
                    lines.append(f"- **Software Requirements:** {', '.join(it.software_requirements)}")
                lines.append("")

        # Alternatives
        lines.append(f"## {sec_num}. Component Alternatives\n")
        sec_num += 1
        if alternatives:
            lines.append("| Alternative Part | Manufacturer | Compatibility | Key Differences | Rationale |")
            lines.append("|---|---|---|---|---|")
            for alt in alternatives:
                diff_str = "; ".join(alt.differences) if alt.differences else "None"
                lines.append(f"| `{alt.part_number}` | {alt.manufacturer} | `{alt.compatibility}` | {diff_str} | {alt.reason} |")
        else:
            lines.append("- No secondary alternatives evaluated.")
        lines.append("")

        # Compatibility & Resource Conflicts
        lines.append(f"## {sec_num}. Compatibility Checks & Resource Conflicts\n")
        sec_num += 1
        if compatibility_checks:
            lines.append("### Compatibility Verifications\n")
            for c in compatibility_checks:
                lines.append(f"- **[{c.status.upper()}] `{c.check_id}` ({c.type}):** {c.description}")
            lines.append("")

        if conflicts:
            lines.append("### Resource Contentions\n")
            for conf in conflicts:
                lines.append(f"- **`{conf.conflict_id}` [{conf.severity.upper()}]:** {conf.description} (*Resolution: {conf.resolution}*)")
            lines.append("")

        # Validation Requirements
        lines.append(f"## {sec_num}. Pre-Procurement Validation Requirements\n")
        sec_num += 1
        lines.append("| Validation ID | Domain | Description | Severity | Status |")
        lines.append("|---|---|---|---|---|")
        for val in validations:
            lines.append(f"| `{val.validation_id}` | `{val.type}` | {val.description} | **{val.severity.upper()}** | `{val.status.upper()}` |")
        lines.append("")

        # Unknowns & Assumptions
        lines.append(f"## {sec_num}. Technical Unknowns & Assumptions\n")
        sec_num += 1
        if unknowns:
            lines.append("### Unknowns")
            for unk in unknowns:
                lines.append(f"- **`{unk.unknown_id}`:** {unk.description} (*Why it matters: {unk.why_it_matters}*)")
            lines.append("")

        if assumptions:
            lines.append("### Engineering Assumptions")
            for asm in assumptions:
                lines.append(f"- **`{asm.assumption_id}`:** {asm.description} (Confidence: `{asm.confidence * 100:.0f}%`)")
            lines.append("")

        # Traceability
        lines.append(f"## {sec_num}. Requirement-to-BOM Traceability\n")
        lines.append("| Traceability ID | Subsystems | Component Requirements | BOM Items | Validations |")
        lines.append("|---|---|---|---|---|")
        for tr in traceability:
            sub_s = ", ".join(tr.subsystem_ids)
            req_s = ", ".join(tr.component_requirement_ids)
            bom_s = ", ".join(tr.bom_item_ids[:3]) + ("..." if len(tr.bom_item_ids) > 3 else "")
            val_s = ", ".join(tr.validation_ids)
            lines.append(f"| `{tr.traceability_id}` | `{sub_s}` | `{req_s}` | `{bom_s}` | `{val_s}` |")
        lines.append("")

        return "\n".join(lines).strip()
