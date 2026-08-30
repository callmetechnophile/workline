"""
File exporter service for EngineeringChangeControlAgent (Section 56).
Generates structured JSON and Markdown change control deliverables.
"""

import json
from pathlib import Path
from typing import List, Optional
from research_agents.engineering_change_control.schemas import (
    ApprovalObject,
    ChangePlan,
    ChangeRequest,
    ImpactObject,
    RiskObject,
)


class ChangeFileExporter:
    """Exports structured change requests, impact analyses, plans, and reports."""

    def export_artifacts(
        self,
        output_dir: str,
        change: ChangeRequest,
        impact: ImpactObject,
        risks: List[RiskObject],
        plan: Optional[ChangePlan] = None,
        approval: Optional[ApprovalObject] = None,
        report_markdown: str = "",
    ) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        # 1. change_request.json
        f1 = out_p / "change_request.json"
        f1.write_text(json.dumps(change.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f1))

        # 2. change_impact.json
        f2 = out_p / "change_impact.json"
        f2.write_text(json.dumps(impact.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f2))

        # 3. change_risks.json
        f3 = out_p / "change_risks.json"
        f3.write_text(json.dumps([r.model_dump() for r in risks], indent=2), encoding="utf-8")
        created_files.append(str(f3))

        # 4. change_plan.json
        f4 = out_p / "change_plan.json"
        plan_data = plan.model_dump() if plan else {"status": "no_plan"}
        f4.write_text(json.dumps(plan_data, indent=2), encoding="utf-8")
        created_files.append(str(f4))

        # 5. change_report.md
        f5 = out_p / "change_report.md"
        f5.write_text(report_markdown, encoding="utf-8")
        created_files.append(str(f5))

        return created_files
