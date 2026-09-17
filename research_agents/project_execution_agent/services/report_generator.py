"""
Markdown Implementation Plan report generator (Agent #10).
"""

from research_agents.project_execution_agent.schemas import ImplementationPlan


class ReportGenerator:
    """Generates structured Markdown report for the complete Implementation Plan."""

    def generate_report(self, plan: ImplementationPlan) -> str:
        lines = [
            f"# Implementation Plan: {plan.title}",
            f"**Plan ID:** `{plan.plan_id}` | **Project ID:** `{plan.project_id}` | **Domain:** {plan.engineering_domain}",
            f"**Total Estimated Effort:** {plan.total_estimated_hours:.1f} Hours | **Execution Readiness:** `{'READY' if plan.execution_readiness else 'BLOCKED'}`",
            "",
            "## 1. Executive Summary & Work Breakdown Structure",
            f"The implementation plan consists of **{len(plan.work_packages)} Work Packages** containing **{len(plan.all_tasks)} discrete tasks**.",
            "",
            "| Work Package ID | Title | Phase | Tasks | Est. Hours |",
            "|---|---|---|---|---|",
        ]
        for wp in plan.work_packages:
            lines.append(f"| `{wp.work_package_id}` | **{wp.title}** | `{wp.phase}` | {len(wp.tasks)} | {wp.estimated_hours:.1f}h |")

        lines.extend([
            "",
            "## 2. Granular Execution Tasks & ArmorIQ Permissions",
            "| Task ID | Work Package | Title | Type | Priority | Dependencies | Allowed Tools | Target File |",
            "|---|---|---|---|---|---|---|---|",
        ])
        for t in plan.all_tasks:
            deps = ", ".join(t.dependencies) if t.dependencies else "None"
            tools = ", ".join(t.allowed_tools)
            target = t.target_file or "N/A"
            lines.append(f"| `{t.task_id}` | `{t.work_package_id}` | {t.title} | `{t.task_type}` | `{t.priority}` | {deps} | `{tools}` | `{target}` |")

        lines.extend([
            "",
            "## 3. Dependency DAG & Critical Path",
            f"- **Topological Order:** `{' -> '.join(plan.dag.topological_order) if plan.dag.topological_order else 'N/A'}`",
            f"- **Critical Path:** `{' -> '.join(plan.dag.critical_path) if plan.dag.critical_path else 'N/A'}`",
            f"- **Cycle Detected:** `{'YES (BLOCKED)' if plan.dag.has_cycle else 'NO (STABLE)'}`",
            "",
            "## 4. Execution Readiness Verdict",
            f"Status: **{'AUTHORIZED FOR AGENT #11 EXECUTION' if plan.execution_readiness else 'BLOCKED BY CIRCULAR DEPENDENCIES'}**",
        ])
        return chr(10).join(lines)
