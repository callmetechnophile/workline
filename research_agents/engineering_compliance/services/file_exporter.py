"""
File exporter service for EngineeringComplianceAgent (Sections 56 & 86).
Generates structured JSON and Markdown compliance deliverables.
"""

import json
from pathlib import Path
from typing import List
from research_agents.engineering_compliance.schemas import (
    ComplianceMatrixItem,
    ComplianceResult,
    ComplianceWaiver,
    ProjectComplianceSummary,
)


class ComplianceFileExporter:
    """Exports structured compliance summaries, results, matrices, waivers, and reports."""

    def export_artifacts(
        self,
        output_dir: str,
        summary: ProjectComplianceSummary,
        results: List[ComplianceResult],
        matrix: List[ComplianceMatrixItem],
        waivers: List[ComplianceWaiver],
        report_markdown: str = "",
    ) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        # 1. compliance_summary.json
        f1 = out_p / "compliance_summary.json"
        f1.write_text(json.dumps(summary.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f1))

        # 2. compliance_results.json
        f2 = out_p / "compliance_results.json"
        f2.write_text(json.dumps([r.model_dump() for r in results], indent=2), encoding="utf-8")
        created_files.append(str(f2))

        # 3. compliance_matrix.json
        f3 = out_p / "compliance_matrix.json"
        f3.write_text(json.dumps([m.model_dump() for m in matrix], indent=2), encoding="utf-8")
        created_files.append(str(f3))

        # 4. compliance_waivers.json
        f4 = out_p / "compliance_waivers.json"
        f4.write_text(json.dumps([w.model_dump() for w in waivers], indent=2), encoding="utf-8")
        created_files.append(str(f4))

        # 5. compliance_gate.json
        f5 = out_p / "compliance_gate.json"
        gate_data = {"project_id": summary.project_id, "gate": summary.gate, "blocking": summary.blocking}
        f5.write_text(json.dumps(gate_data, indent=2), encoding="utf-8")
        created_files.append(str(f5))

        # 6. compliance_report.md
        f6 = out_p / "compliance_report.md"
        f6.write_text(report_markdown, encoding="utf-8")
        created_files.append(str(f6))

        return created_files
