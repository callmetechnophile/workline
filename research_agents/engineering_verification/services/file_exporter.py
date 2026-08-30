"""
File exporter service for EngineeringVerificationAgent (Section 83).
Generates structured JSON and Markdown verification deliverables.
"""

import json
from pathlib import Path
from typing import List
from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    TestResult,
    VerificationCoverage,
    VerificationMatrixItem,
    VerificationPlan,
)


class VerificationFileExporter:
    """Exports structured verification plans, results, matrices, evidence, and reports."""

    def export_artifacts(
        self,
        output_dir: str,
        plan: VerificationPlan,
        coverage: VerificationCoverage,
        results: List[TestResult],
        matrix: List[VerificationMatrixItem],
        evidence: List[EvidenceObject],
        report_markdown: str = "",
    ) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        # 1. verification_plan.json
        f1 = out_p / "verification_plan.json"
        f1.write_text(json.dumps(plan.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f1))

        # 2. verification_report.json
        f2 = out_p / "verification_report.json"
        f2.write_text(json.dumps(coverage.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f2))

        # 3. verification_matrix.json
        f3 = out_p / "verification_matrix.json"
        f3.write_text(json.dumps([m.model_dump() for m in matrix], indent=2), encoding="utf-8")
        created_files.append(str(f3))

        # 4. test_results.json
        f4 = out_p / "test_results.json"
        f4.write_text(json.dumps([r.model_dump() for r in results], indent=2), encoding="utf-8")
        created_files.append(str(f4))

        # 5. evidence_index.json
        f5 = out_p / "evidence_index.json"
        f5.write_text(json.dumps([ev.model_dump() for ev in evidence], indent=2), encoding="utf-8")
        created_files.append(str(f5))

        # 6. verification_report.md
        f6 = out_p / "verification_report.md"
        f6.write_text(report_markdown, encoding="utf-8")
        created_files.append(str(f6))

        return created_files
