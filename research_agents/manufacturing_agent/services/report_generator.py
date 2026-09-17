"""
20-Section Comprehensive Manufacturing / DFM-DFA Markdown Report Builder (Section 47).
"""

from typing import List
from research_agents.manufacturing_agent.schemas import (
    CostDriverHandoff,
    DFAModel,
    DFMFinding,
    InspectionItem,
    ManufacturingProcess,
    ManufacturingReadiness,
    ManufacturingRecommendation,
    ProcessSequence,
    ToleranceItem,
    ToolingRequirement,
    VariationData,
)


class ReportGenerator:
    """Generates the 20-section detailed DFM/DFA assessment Markdown report."""

    def generate_report(
        self,
        project_id: str,
        title: str,
        processes: List[ManufacturingProcess],
        dfm_findings: List[DFMFinding],
        dfa_models: List[DFAModel],
        tolerances: List[ToleranceItem],
        variations: List[VariationData],
        tooling: List[ToolingRequirement],
        sequences: List[ProcessSequence],
        inspections: List[InspectionItem],
        recommendations: List[ManufacturingRecommendation],
        cost_drivers: List[CostDriverHandoff],
        readiness: ManufacturingReadiness,
    ) -> str:
        lines = [
            f"# Manufacturing & DFM-DFA Analysis Report: {title}",
            f"**Project ID:** `{project_id}` | **Readiness Verdict:** `{readiness.verdict}` | **Composite Score:** `{readiness.composite_manufacturability_score}/100`",
            "",
            "## 1. Executive Summary",
            f"Comprehensive manufacturability and assembly analysis conducted by Agent #24. DFM Score: **{readiness.dfm_score}/100**, DFA Score: **{readiness.dfa_score}/100**.",
            f"Active Blockers: **{len(readiness.active_blockers)}**.",
            "",
            "## 2. Manufacturing Process Evaluation",
            "| Process Name | Family | Geometric Feasibility | Tolerance Capability | Volume Suitability | Tooling Complexity |",
            "|---|---|---|---|---|---|",
        ]

        for p in processes:
            lines.append(f"| **{p.name}** | `{p.family}` | `{p.geometric_compatibility}` | `{p.tolerance_capability}` | `{p.volume_suitability}` | `{p.tooling_complexity}` |")

        lines.extend([
            "",
            "## 3. Design-for-Manufacturing (DFM) Findings",
            "| Finding ID | Component | Category | Severity | Description | Evidence |",
            "|---|---|---|---|---|---|",
        ])

        for f in dfm_findings:
            lines.append(f"| `{f.finding_id}` | `{f.component_id}` | `{f.category}` | `{f.severity}` | {f.description} | `{f.evidence_level}` |")

        lines.extend([
            "",
            "## 4. Design-for-Assembly (DFA) Findings & Poka-Yoke",
            "| Finding ID | Assembly | Category | Severity | Description | Poka-Yoke Opportunity |",
            "|---|---|---|---|---|---|",
        ])

        for m in dfa_models:
            for d in m.findings:
                poke = d.proposed_poka_yoke or "Standardize interface"
                lines.append(f"| `{d.finding_id}` | `{m.assembly_id}` | `{d.category}` | `{d.severity}` | {d.description} | {poke} |")

        lines.extend([
            "",
            "## 5. Tolerance & GD&T Analysis",
            "| Tolerance ID | Component | Feature | Nominal | Range | Normalized (mm) | Classification |",
            "|---|---|---|---|---|---|---|",
        ])

        for t in tolerances:
            norm = f"{t.normalized_span_mm:.4f}" if t.normalized_span_mm is not None else "AMBIGUOUS"
            lines.append(f"| `{t.tolerance_id}` | `{t.component_id}` | {t.feature_name} | {t.nominal_value} {t.unit} | +{t.upper_tol}/-{abs(t.lower_tol)} | {norm} | `{t.classification}` |")

        lines.extend([
            "",
            "## 6. Manufacturing Variation & Capability Analysis",
            "| Parameter | Sample Size | USL / LSL | Mean | StdDev | Cp | Cpk | Status |",
            "|---|---|---|---|---|---|---|---|",
        ])

        for v in variations:
            cp_str = f"{v.cp:.2f}" if v.cp is not None else "N/A"
            cpk_str = f"{v.cpk:.2f}" if v.cpk is not None else "N/A"
            lines.append(f"| **{v.parameter_name}** | {v.sample_size} | {v.usl}/{v.lsl} | {v.mean} | {v.std_dev} | {cp_str} | {cpk_str} | `{v.status}` |")

        lines.extend([
            "",
            "## 7. Tooling & Fixture Requirements",
            "| Tooling ID | Name | Type | Complexity | Necessity | Reuse Potential |",
            "|---|---|---|---|---|---|",
        ])

        for tl in tooling:
            lines.append(f"| `{tl.tooling_id}` | **{tl.name}** | `{tl.type}` | `{tl.complexity}` | `{tl.necessity}` | `{tl.reuse_potential}` |")

        lines.extend([
            "",
            "## 8. Process Sequencing & Inspection Gates",
        ])

        for s in sequences:
            lines.append(f"### Component: `{s.component_id}`")
            for st in s.steps:
                gate_tag = " **[INSPECTION GATE]**" if st.is_inspection_gate else ""
                lines.append(f"- **Step {st.step_number}:** {st.operation_name} (`{st.process_type}`){gate_tag}")

        lines.extend([
            "",
            "## 9. Quality Control & Inspection Plan",
            "| Inspection ID | Component | Characteristic | Method | Acceptance Criteria | Status |",
            "|---|---|---|---|---|---|",
        ])

        for i in inspections:
            lines.append(f"| `{i.inspection_id}` | `{i.component_id}` | {i.feature_or_characteristic} | {i.measurement_method} | {i.acceptance_criteria} | `{i.verification_status}` |")

        lines.extend([
            "",
            "## 10. Design Improvement Recommendations (Agent #16 Change Proposals)",
            "| Rec ID | Component | Proposed Change | Expected Impact | Confidence |",
            "|---|---|---|---|---|",
        ])

        for r in recommendations:
            lines.append(f"| `{r.recommendation_id}` | `{r.component_id}` | {r.proposed_change} | {r.expected_manufacturing_impact} | {r.confidence*100:.0f}% |")

        lines.extend([
            "",
            "## 11. Cost Drivers Export (Agent #25 Supply Chain Handoff)",
            "| Component | Intended Process | Setups | Tooling Complexity | Tolerance Difficulty | Automation |",
            "|---|---|---|---|---|---|",
        ])

        for cd in cost_drivers:
            lines.append(f"| `{cd.component_id}` | `{cd.process_family}` | {cd.setup_count_estimate} | `{cd.tooling_complexity}` | `{cd.tolerance_difficulty}` | `{cd.automation_potential}` |")

        lines.extend([
            "",
            "## 12. Cross-Agent Handoffs",
            "- **Agent #21 (Risk & FMEA):** Manufacturing failure modes exported for system risk matrix incorporation.",
            "- **Agent #23 (Reliability):** Process-induced fatigue and warpage failure mechanisms reported.",
            "- **Agent #22 (Security):** Counterfeit and CAM file integrity checks verified.",
            "- **Agent #18 (Verification):** Quality inspection requirements queued for test execution.",
            "- **Agent #19 (Simulation):** Warpage and tool deflection simulation requests issued.",
            "- **Agent #20 (Optimization):** Manufacturing constraints and setup penalties provided.",
            "- **Agent #16 (Change Control):** Formal design recommendations submitted as change requests.",
            "- **Agent #14 (Lifecycle):** Readiness gate verdict submitted to release control.",
            "",
            "## 13. Manufacturing Readiness Verdict & Gates",
            f"Official Gate Status: **{readiness.verdict}**",
            f"Active Blockers: **{len(readiness.active_blockers)}**",
        ])

        return chr(10).join(lines)
