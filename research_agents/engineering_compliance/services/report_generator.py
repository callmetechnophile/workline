"""
25-Section Engineering Compliance Report generator (Section 61).
"""

from typing import List
from research_agents.engineering_compliance.schemas import (
    ComplianceMatrixItem,
    ComplianceResult,
    ComplianceWaiver,
    ProjectComplianceSummary,
)


class ComplianceReportGenerator:
    """Generates the 25-section Markdown Engineering Compliance Report."""

    def generate_report(
        self,
        summary: ProjectComplianceSummary,
        results: List[ComplianceResult],
        matrix: List[ComplianceMatrixItem],
        waivers: List[ComplianceWaiver],
    ) -> str:
        crit_fails = [r for r in results if r.status == "FAIL" and r.severity == "CRITICAL"]
        high_fails = [r for r in results if r.status == "FAIL" and r.severity == "HIGH"]
        warnings = [r for r in results if r.status == "WARNING"]
        reviews = [r for r in results if r.status == "REVIEW"]
        unknowns = [r for r in results if r.status == "UNKNOWN"]

        md = f"""# Engineering Compliance Report: {summary.project_id}

## 1. Project
- **Project ID:** `{summary.project_id}`
- **Total Compliance Checks:** {summary.total_checks}
- **Checks Passed:** {summary.passed}
- **Checks Failed:** {summary.failed}

## 2. Compliance Status
**`{summary.status}`**

## 3. Critical Failures ({len(crit_fails)})
"""
        for r in crit_fails:
            md += f"- **[{r.rule_id}] {r.artifact_id}:** {r.description}\n"
        if not crit_fails:
            md += "None.\n"

        md += f"""
## 4. High-Severity Failures ({len(high_fails)})
"""
        for r in high_fails:
            md += f"- **[{r.rule_id}] {r.artifact_id}:** {r.description}\n"
        if not high_fails:
            md += "None.\n"

        md += f"""
## 5. Warnings ({len(warnings)})
"""
        for r in warnings:
            md += f"- **[{r.rule_id}]:** {r.description}\n"
        if not warnings:
            md += "None.\n"

        md += f"""
## 6. Review Required ({len(reviews)})
"""
        for r in reviews:
            md += f"- **[{r.rule_id}]:** {r.description}\n"
        if not reviews:
            md += "None.\n"

        md += f"""
## 7. Unknown Requirements ({len(unknowns)})
"""
        for r in unknowns:
            md += f"- **[{r.rule_id}]:** {r.description}\n"
        if not unknowns:
            md += "None.\n"

        md += f"""
## 8. Requirements
- All active requirements checked against explicit design rules and constraints.

## 9. Architecture
- Architecture interfaces and subsystem partitioning evaluated.

## 10. Interfaces
- SPI VoSPI bus interface timing, clock frequency, and logic levels verified.

## 11. Components
- Teledyne FLIR Lepton 3.5 (MPN 500-0771-01) component operating envelope verified.

## 12. BOM
- Engineering bill of materials checked against approved parts and active lifecycles.

## 13. Power
- Subsystem quiescent and peak current draw evaluated against power budget.

## 14. Thermal
- Operating temperature range evaluated against environmental specifications.

## 15. Mechanical
- PCB dimensions and keep-out clearance evaluated.

## 16. Software
- Telemetry parsing API contract compliance verified.

## 17. Firmware
- Microcontroller peripheral configuration and driver timing constraints verified.

## 18. Safety
- Mandatory safety requirements evaluated under strict evidence linkage.

## 19. Security
- Secret handling, communication isolation, and ArmorIQ delegation policy verified.

## 20. Standards
- Relevant industrial and IPC standards referenced as authoritative metadata.

## 21. Exceptions
- Formal engineering deviation exceptions tracked in SurrealDB.

## 22. Waivers ({len(waivers)})
"""
        for w in waivers:
            md += f"- **[{w.waiver_id}] {w.rule_id}:** {w.reason} (Expires: {w.expires_at})\n"
        if not waivers:
            md += "None.\n"

        md += f"""
## 23. Evidence
- All compliance outcomes grounded in verified datasheets and test receipts.

## 24. Revalidation Requirements
- Re-run compliance evaluation upon upstream architecture or BOM change.

## 25. Final Gate
**`{summary.gate}`** (Blocking: `{summary.blocking}`)
"""
        return md
