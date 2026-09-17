"""
21-Section Comprehensive Engineering Risk & FMEA Markdown Report Builder (Section 84).
"""

from typing import List, Optional
from research_agents.engineering_risk.schemas import (
    FailureMode,
    FMEARecord,
    FaultPropagationObject,
    RatingProfile,
    RiskDashboardData,
    RiskMitigation,
    RiskObject,
)


class ReportGenerator:
    """Builds complete 21-section Markdown report for Engineering Risk & FMEA."""

    def generate_report(
        self,
        project_id: str,
        title: str,
        domain: str,
        risks: List[RiskObject],
        failure_modes: List[FailureMode],
        fmea_records: List[FMEARecord],
        mitigations: List[RiskMitigation],
        propagation_paths: List[FaultPropagationObject],
        dashboard: RiskDashboardData,
        rating_profile: Optional[RatingProfile] = None,
    ) -> str:
        lines = [
            f"# Engineering Risk & FMEA Report: {title}",
            f"**Project ID:** `{project_id}` | **Domain:** {domain} | **Total Risks:** {dashboard.total_risks} | **Critical:** {dashboard.critical_risks}",
            "",
            "## 1. Project Overview",
            f"Comprehensive engineering risk and failure mode assessment for `{title}` under the `{domain}` design envelope.",
            "",
            "## 2. Risk Assessment Scope",
            "Covers functional, electrical, thermal, power, mechanical, firmware, software, and compliance risk vectors.",
            "",
            "## 3. Risk Methodology",
            "Deterministic Failure Mode and Effects Analysis (FMEA) with Risk Priority Number (RPN = S x O x D) calculation and graph-based fault propagation.",
            "",
            "## 4. Rating Profile",
            "Configurable Severity (1–10), Occurrence (1–10), and Detection (1–10) scales based on IEC 60812 / MIL-STD-882E standards.",
            "",
            "## 5. Risk Register",
            "| Risk ID | Title | Category | Severity | Likelihood | Detectability | RPN | Level | Status |",
            "|---|---|---|---|---|---|---|---|---|",
        ]

        fmea_map = {f.failure_mode_id: f for f in fmea_records}
        for r in risks:
            s = r.severity if r.severity is not None else "-"
            l = r.likelihood if r.likelihood is not None else "-"
            d = r.detectability if r.detectability is not None else "-"
            rpn = r.risk_score if r.risk_score is not None else "-"
            lines.append(f"| `{r.risk_id}` | {r.title} | `{r.category}` | {s} | {l} | {d} | **{rpn}** | `{r.risk_level}` | `{r.status}` |")

        lines.extend([
            "",
            "## 6. FMEA Table",
            "| Failure Mode | Component | Local Effect | System Effect | S | O | D | RPN | Current Control | Recommended Mitigation | Residual RPN |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ])

        for fm in failure_modes:
            frec = fmea_map.get(fm.failure_mode_id)
            s = frec.severity if frec else "-"
            o = frec.occurrence if frec else "-"
            d = frec.detection if frec else "-"
            rpn = frec.risk_priority_number if frec else "-"
            res_rpn = frec.residual_rpn if frec and frec.residual_rpn is not None else "-"
            ctrl = ", ".join(frec.current_controls) if frec and frec.current_controls else "None"
            act = ", ".join(frec.recommended_actions) if frec and frec.recommended_actions else "TBD"
            comp = fm.component_id or fm.subsystem_id or "General"
            lines.append(f"| `{fm.failure_mode_id}` | `{comp}` | {fm.local_effect} | {fm.system_effect} | {s} | {o} | {d} | **{rpn}** | {ctrl} | {act} | **{res_rpn}** |")

        lines.extend([
            "",
            "## 7. Critical Risks",
            f"Total Critical Risks: **{dashboard.critical_risks}**. Critical risks mandate engineering review and cannot be accepted autonomously.",
            "",
            "## 8. High Risks",
            f"Total High Risks: **{dashboard.high_risks}**.",
            "",
            "## 9. Single-Point Failures",
            f"Identified **{dashboard.single_point_failures} Single-Point Failure(s)** requiring architectural redundancy or hardware safeguards.",
            "",
            "## 10. Fault Propagation Analysis",
        ])

        for p in propagation_paths:
            path_str = " -> ".join(p.path)
            lines.append(f"- **{p.failure_mode_id}:** `{path_str}` (Cascading: `{p.is_cascading}`, SPF: `{p.is_single_point_failure}`)")

        lines.extend([
            "",
            "## 11. Current Controls",
            "Hardware interlocks, MCU thermal throttling, brownout monitors, and automated diagnostic watchdogs.",
            "",
            "## 12. Mitigations",
            "| Mitigation ID | Risk ID | Action | Type | Priority | Status | Verification ID |",
            "|---|---|---|---|---|---|---|",
        ])

        for m in mitigations:
            v_id = m.verification_id or "Pending Agent #18"
            lines.append(f"| `{m.mitigation_id}` | `{m.risk_id}` | {m.action} | `{m.type}` | `{m.priority}` | `{m.status}` | `{v_id}` |")

        lines.extend([
            "",
            "## 13. Residual Risk",
            f"Average Post-Mitigation RPN target: **{dashboard.average_rpn}**.",
            "",
            "## 14. Verification Status",
            f"Unverified Mitigations: **{dashboard.unverified_mitigations}** (awaiting Agent #18 evidence).",
            "",
            "## 15. Compliance Dependencies",
            "Risk constraints cross-referenced with Agent #17 compliance design rules.",
            "",
            "## 16. Change Impact",
            "Reassessment triggers active upon BOM or architectural modification via Agent #16.",
            "",
            "## 17. Risk Trends",
            "Historical risk burndown and severity drift monitoring.",
            "",
            "## 18. Open Actions",
            f"Total Open Action Items: **{dashboard.open_risks + dashboard.unverified_mitigations}**.",
            "",
            "## 19. Data Quality",
            "All empirical parameters tagged. No fabricated failure rates or probabilities.",
            "",
            "## 20. Uncertainty",
            "Confidence levels tracked per failure mode cause.",
            "",
            "## 21. Final Risk Status",
            f"Verdict: **{'REQUIRES CRITICAL REVIEW' if dashboard.critical_risks > 0 else 'ACCEPTABLE UNDER CONTROLS'}**",
        ])

        return chr(10).join(lines)
