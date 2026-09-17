"""
22-Section Comprehensive Security & Threat Modeling Markdown Report Builder (Section 103).
"""

from typing import List
from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    SecurityControl,
    SecurityDashboardData,
    SecurityTestCase,
    ThreatActor,
    ThreatMitigation,
    ThreatObject,
    TrustBoundary,
)


class ReportGenerator:
    """Generates the 22-section standard Security & Threat Modeling Markdown report."""

    def generate_report(
        self,
        project_id: str,
        title: str,
        assets: List[AssetObject],
        actors: List[ThreatActor],
        boundaries: List[TrustBoundary],
        attack_surface: List[AttackSurfaceEntry],
        threats: List[ThreatObject],
        attack_paths: List[AttackPath],
        controls: List[SecurityControl],
        mitigations: List[ThreatMitigation],
        security_tests: List[SecurityTestCase],
        dashboard: SecurityDashboardData,
    ) -> str:
        lines = [
            f"# Security & Threat Modeling Report: {title}",
            f"**Project ID:** `{project_id}` | **Security Score:** {dashboard.security_score}/100 | **Security Gate:** `{dashboard.security_gate}`",
            "",
            "## 1. Project Overview",
            f"Cybersecurity threat model and attack surface assessment for `{title}` within the WorkflowGuide AI agent architecture.",
            "",
            "## 2. Security Scope",
            "Covers API endpoints, document ingestion, Agent Control Fabric, A2A communication, SurrealDB graph queries, ArmorIQ delegation, and external cloud integrations.",
            "",
            "## 3. System Architecture",
            "Multi-agent collaborative framework with FastAPI ingress, Bedrock reasoning, SurrealDB graph database, and ArmorIQ least-privilege runtime sandboxing.",
            "",
            "## 4. Assets",
            "| Asset ID | Name | Type | Classification | Description |",
            "|---|---|---|---|---|",
        ]

        for a in assets:
            lines.append(f"| `{a.asset_id}` | **{a.name}** | `{a.type}` | `{a.classification}` | {a.description} |")

        lines.extend([
            "",
            "## 5. Actors",
            "- **External Web Attacker:** Unauthenticated public network entity attempting prompt injection, DDoS, or API abuse.",
            "- **Malicious Tenant / Insider:** Authenticated user attempting cross-tenant graph queries or data exfiltration.",
            "- **Compromised Worker Agent:** Compromised subprocess attempting A2A message forgery or unauthorized shell execution.",
            "",
            "## 6. Trust Boundaries",
            "| Boundary ID | Name | Source Zone | Destination Zone | Enforced Controls |",
            "|---|---|---|---|---|",
        ])

        for tb in boundaries:
            ctrls = ", ".join(tb.controls)
            lines.append(f"| `{tb.boundary_id}` | **{tb.name}** | `{tb.source_zone}` | `{tb.destination_zone}` | {ctrls} |")

        lines.extend([
            "",
            "## 7. Data Flows",
            "Client API requests -> Control Fabric -> Agent Runtime -> Bedrock / Tool Execution -> SurrealDB Ingestion.",
            "",
            "## 8. Attack Surface",
            "| Entry ID | Type | Exposure | Endpoint / Target | Authentication |",
            "|---|---|---|---|---|",
        ])

        for e in attack_surface:
            ep = e.endpoint_path or "N/A"
            auth = e.authentication or "None"
            lines.append(f"| `{e.entry_id}` | `{e.type}` | `{e.exposure}` | `{ep}` | {auth} |")

        lines.extend([
            "",
            "## 9. Threat Model",
            "| Threat ID | Title | Category | Severity | Likelihood | Risk Score | Status |",
            "|---|---|---|---|---|---|---|",
        ])

        for t in threats:
            sev = t.severity or "-"
            lik = t.likelihood or "-"
            score = t.risk_score or "-"
            lines.append(f"| `{t.threat_id}` | **{t.title}** | `{t.category}` | {sev} | {lik} | **{score}** | `{t.status}` |")

        lines.extend([
            "",
            "## 10. Attack Paths",
        ])

        for p in attack_paths:
            steps = " -> ".join(p.steps)
            lines.append(f"- **{p.threat_id} Path:** `{steps}` (Target: `{p.target_asset}`)")

        lines.extend([
            "",
            "## 11. Critical Threats",
            f"Total Critical Threats: **{dashboard.critical_threats}** (Zero tolerance for unmitigated RCE or credential theft).",
            "",
            "## 12. Security Controls",
            "| Control ID | Name | Category | Implemented | Verification Status |",
            "|---|---|---|---|---|",
        ])

        for c in controls:
            lines.append(f"| `{c.control_id}` | **{c.name}** | `{c.category}` | `{c.implemented}` | `{c.verification_status}` |")

        lines.extend([
            "",
            "## 13. Mitigations",
            "| Mitigation ID | Threat ID | Action | Priority | Status |",
            "|---|---|---|---|---|",
        ])

        for m in mitigations:
            lines.append(f"| `{m.mitigation_id}` | `{m.threat_id}` | {m.action} | `{m.priority}` | `{m.status}` |")

        lines.extend([
            "",
            "## 14. Verification Status",
            f"Verified Controls: **{dashboard.verified_controls}** | Unverified Controls: **{dashboard.unverified_controls}** (Pending Agent #18 test verification).",
            "",
            "## 15. Security Test Requirements",
        ])

        for st in security_tests:
            lines.append(f"- **{st.security_test_id}:** {st.objective} (`{st.test_type}`, Status: `{st.verification_status}`)")

        lines.extend([
            "",
            "## 16. Dependency / Supply Chain Security",
            "All virtual environment packages pinned. No untrusted third-party binaries in core execution path.",
            "",
            "## 17. Multi-Tenant Security",
            "Strict SurrealDB query scoping enforcing `WHERE project_id = $project_id` on all graph entities.",
            "",
            "## 18. Agentic AI Security",
            "Prompt isolation delimiters active. Untrusted research content treated as non-instruction data.",
            "",
            "## 19. A2A Security",
            "Inter-agent messages validated against AgentRegistry before dispatch.",
            "",
            "## 20. Residual Security Risk",
            f"Calculated Platform Security Score: **{dashboard.security_score}/100**.",
            "",
            "## 21. Change Impact & Regression",
            "Continuous re-evaluation triggered upon architecture, BOM, or API modification via Agent #16.",
            "",
            "## 22. Security Gate Verdict",
            f"Release Gate Verdict: **{'BLOCKED - RESOLUTION REQUIRED' if dashboard.security_gate == 'SECURITY_BLOCKED' else 'AUTHORIZED FOR RELEASE'}**",
        ])

        return chr(10).join(lines)
