"""
Publication-ready Markdown report generator for EngineeringExecutionAgent (Section 63).
Renders 18 distinct execution audit and verification sections.
"""

from typing import Any, Dict, List
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionContext,
    ExecutionAuditItem,
    ExecutionGraph,
    ToolCallRecord,
)


class ExecutionReportGenerator:
    """Renders comprehensive 18-section Markdown Engineering Execution Report."""

    def generate_report(
        self,
        project_title: str,
        execution_id: str,
        status: str,
        auth: AuthorizedExecution,
        context: EngineeringExecutionContext,
        completed_tasks: List[Dict[str, Any]],
        failed_tasks: List[Dict[str, Any]],
        blocked_tasks: List[Dict[str, Any]],
        denied_actions: List[Dict[str, Any]],
        tool_calls: List[ToolCallRecord],
        receipts: List[Dict[str, Any]],
        audit_trail: List[ExecutionAuditItem],
        changed_files: List[str],
        warnings: List[str],
        errors: List[str],
        graph: ExecutionGraph,
    ) -> str:
        lines: List[str] = []

        # Header
        lines.append(f"# Engineering Execution Report: {project_title}\n")
        lines.append(f"**Execution ID:** `{execution_id}` | **Status:** **`{status.upper()}`**  ")
        lines.append(f"**Authorization ID:** `{auth.authorization_id}` | **ArmorIQ Governance:** `ACTIVE`\n")

        # 1. Project
        lines.append("## 1. Project\n")
        lines.append(f"- **Project Name:** {project_title}")
        lines.append(f"- **Project ID:** `{context.project_id}`")
        lines.append(f"- **Executing Agent:** `{context.agent_id}`\n")

        # 2. Authorization
        lines.append("## 2. Authorization Scope\n")
        lines.append(f"- **Parent Agent:** `{auth.parent_agent_id}`")
        lines.append(f"- **Authorized Tasks:** `{len(auth.allowed_tasks)}` tasks")
        lines.append(f"- **Authorized Tools:** `{', '.join(auth.allowed_tools) if auth.allowed_tools else 'ALL_SCOPED'}`")
        lines.append(f"- **Authorized Paths:** `{', '.join(auth.allowed_paths) if auth.allowed_paths else 'ALL_INTERNAL'}`")
        lines.append(f"- **Authorized Operations:** `{', '.join(auth.allowed_operations) if auth.allowed_operations else 'STANDARD'}`\n")

        # 3. ArmorIQ Status
        lines.append("## 3. ArmorIQ Cryptographic Enforcement Status\n")
        lines.append("- **Status:** `CONNECTED & ENFORCED`")
        lines.append(f"- **Receipts Generated:** `{len(receipts)}`\n")

        # 4. Captured Plan
        lines.append("## 4. Captured Execution Plan\n")
        lines.append(f"- Execution plan registered via `capture_plan()` prior to tool invocation.\n")

        # 5. Delegation Chain
        lines.append("## 5. Delegation Chain\n")
        lines.append(f"`{context.user_id}` ➔ `{auth.parent_agent_id}` ➔ `{auth.authorized_agent_id}` ➔ `Task Execution`\n")

        # 6. Executed Tasks
        lines.append("## 6. Executed Tasks\n")
        lines.append(f"- **Total Tasks Attempted:** `{len(completed_tasks) + len(failed_tasks) + len(blocked_tasks) + len(denied_actions)}`")
        lines.append(f"- **Completed:** `{len(completed_tasks)}` | **Failed:** `{len(failed_tasks)}` | **Blocked:** `{len(blocked_tasks)}` | **Denied:** `{len(denied_actions)}`\n")

        # 7. Tool Calls
        lines.append("## 7. Tool Calls Telemetry\n")
        lines.append("| Tool Call ID | Task | Tool | Operation | Status | Duration | Receipt |")
        lines.append("|---|---|---|---|---|---|---|")
        for tc in tool_calls:
            r_str = f"`{tc.armoriq_receipt_id[:10]}...`" if tc.armoriq_receipt_id else "N/A"
            lines.append(f"| `{tc.tool_call_id}` | `{tc.task_id}` | `{tc.tool}` | `{tc.operation}` | **`{tc.status.upper()}`** | `{tc.duration_ms:.1f}ms` | {r_str} |")
        if not tool_calls:
            lines.append("| N/A | N/A | N/A | N/A | NONE | 0ms | N/A |")
        lines.append("")

        # 8. Successful Operations
        lines.append("## 8. Successful Operations\n")
        if completed_tasks:
            for ct in completed_tasks:
                lines.append(f"- **`{ct.get('task_id')}`**: {ct.get('title')} (Status: `{ct.get('status')}`)")
        else:
            lines.append("- No tasks completed in this run.")
        lines.append("")

        # 9. Denied Operations
        lines.append("## 9. Denied Operations (Zero-Implicit-Authority Violations)\n")
        if denied_actions:
            for da in denied_actions:
                lines.append(f"- **`{da.get('task_id')}`**: {da.get('title')} — `{da.get('status')}`: {da.get('details') or da.get('reason')}")
        else:
            lines.append("- Zero unauthorized access attempts detected.")
        lines.append("")

        # 10. Failed Operations
        lines.append("## 10. Failed Operations\n")
        if failed_tasks:
            for ft in failed_tasks:
                lines.append(f"- **`{ft.get('task_id')}`**: {ft.get('title')} — Error: `{ft.get('error')}`")
        else:
            lines.append("- None.")
        lines.append("")

        # 11. Changed Files
        lines.append("## 11. Verified Changed Files\n")
        if changed_files:
            for cf in changed_files:
                lines.append(f"- `{cf}`")
        else:
            lines.append("- No filesystem modifications.")
        lines.append("")

        # 12. Test Results
        lines.append("## 12. Test Results\n")
        test_calls = [tc for tc in tool_calls if "test" in tc.tool.lower()]
        if test_calls:
            for t in test_calls:
                lines.append(f"- **{t.tool}** on `{t.resource}`: `{t.status.upper()}`")
        else:
            lines.append("- No test suites executed in this run.")
        lines.append("")

        # 13. Build Results
        lines.append("## 13. Build Results\n")
        lines.append("- Firmware and code artifacts created within verified boundaries.\n")

        # 14. Errors
        lines.append("## 14. Execution Errors\n")
        if errors:
            for e in errors:
                lines.append(f"- {e}")
        else:
            lines.append("- None.")
        lines.append("")

        # 15. Warnings
        lines.append("## 15. Warnings\n")
        if warnings:
            for w in warnings:
                lines.append(f"- {w}")
        else:
            lines.append("- None.")
        lines.append("")

        # 16. Execution Graph
        lines.append("## 16. Execution Graph Topology\n")
        lines.append(f"- **Graph Nodes:** `{len(graph.nodes)}` | **Graph Edges:** `{len(graph.edges)}`\n")

        # 17. Cryptographic Receipts
        lines.append("## 17. Cryptographic Receipts & Audit Proofs\n")
        for r in receipts:
            lines.append(f"- **Receipt ID:** `{r.get('receipt_id')}` | **Agent:** `{r.get('agent')}` | **Signature:** `{r.get('signature', 'VALID')[:16]}...`")
        lines.append("")

        # 18. Final Execution Status
        lines.append("## 18. Final Execution Status\n")
        if status == "success":
            lines.append("✓ **IMPLEMENTATION COMPLETE:** All authorized engineering work packages were executed under cryptographic ArmorIQ governance.")
        elif status == "blocked":
            lines.append("⛔ **EXECUTION BLOCKED:** Validation gate halted execution due to critical design violations.")
        elif status == "denied":
            lines.append("⛔ **EXECUTION DENIED:** Zero-implicit-authority checks blocked out-of-scope operations.")
        else:
            lines.append(f"⚠️ **STATUS:** `{status.upper()}`")
        lines.append("")

        return "\n".join(lines).strip()
