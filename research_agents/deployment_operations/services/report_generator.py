"""
20-Section Structured Deployment & Operations Engineering Report Generator.
"""

from research_agents.deployment_operations.schemas import DeploymentOpsOutput


class ReportGenerator:
    """Renders authoritative Markdown engineering deployment & operations report."""

    def generate_full_report(self, out: DeploymentOpsOutput) -> str:
        lines = []
        lines.append(f"# Deployment & Operations Analysis Report — {out.system_id}")
        lines.append(f"**Project**: `{out.project_id}` | **System Type**: `{out.system_type.value}`")
        lines.append(f"**Deployment Readiness Status**: **{out.readiness_status.value}**\n")

        lines.append("## 1. Executive Summary")
        lines.append(
            f"This operational engineering evaluation assesses the deployability, commissioning, "
            f"monitoring, maintenance, and recovery readiness for system `{out.system_id}`. "
            f"Overall readiness is currently evaluated as **{out.readiness_status.value}**."
        )
        lines.append("")

        lines.append("## 2. Deployment Readiness Criteria")
        for c in out.readiness_criteria:
            status_badge = f"[{c.status.value}]"
            block_flag = " **[BLOCKER]**" if c.is_blocking else ""
            lines.append(f"- {status_badge}{block_flag} **{c.name}** ({c.category}): {c.notes or c.blocking_reason or 'Evaluated'}")
        lines.append("")

        lines.append("## 3. Sequenced Deployment Plan")
        if out.deployment_plan:
            for s in out.deployment_plan.steps:
                auth_badge = " *(Requires ArmorIQ Authorization)*" if s.requires_authorization else ""
                lines.append(f"### Step {s.step_number}: {s.title}{auth_badge}")
                lines.append(f"- **Action**: {s.action}")
                lines.append(f"- **Responsible Role**: `{s.responsible_role}`")
                lines.append(f"- **Expected Result**: {s.expected_result}")
                lines.append(f"- **Rollback Action**: {s.rollback_action or 'None'}")
        lines.append("")

        lines.append("## 4. Commissioning Test Matrix")
        if out.commissioning_plan:
            for t in out.commissioning_plan.tests:
                lines.append(f"- **[{t.status.value}] {t.test_id}**: {t.name} (Subsystem: `{t.subsystem}`) -> *{t.expected_result}*")
        lines.append("")

        lines.append("## 5. Health Monitoring & Alert Rules")
        for a in out.alert_rules:
            lines.append(f"- **[{a.severity.value}] {a.rule_id}**: {a.name} *(Trigger: {a.condition})*")
            lines.append(f"  - **Response**: {a.response_procedure}")
        lines.append("")

        lines.append("## 6. Maintenance & Serviceability Schedule")
        for m in out.maintenance_tasks:
            lines.append(f"- **[{m.maintenance_type.value}] {m.task_id}**: {m.action} on `{m.component_id}` (Interval: {m.interval})")
            lines.append(f"  - **Safety Precaution**: {m.safety_prerequisite}")
        lines.append("")

        lines.append("## 7. Critical Spare Parts Requirements")
        for sp in out.spare_parts:
            ss_flag = " (Single Source)" if sp.is_single_source else ""
            lines.append(f"- **{sp.part_id}**: {sp.part_name} — Recommended On-site: {sp.recommended_stock_qty} units (Lead Time: {sp.lead_time_weeks or 'N/A'} wks){ss_flag}")
        lines.append("")

        lines.append("## 8. Decommissioning & Retirement Procedures")
        if out.decommissioning_plan:
            for step in out.decommissioning_plan.shutdown_sequence:
                lines.append(f"- {step}")

        return "\n".join(lines)
