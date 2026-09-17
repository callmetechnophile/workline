"""
File Exporter for Manufacturing Deliverables (Section 43).
"""

import csv
import json
from pathlib import Path
from typing import List, Optional
from loguru import logger

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


class FileExporter:
    """Exports structured manufacturing artifacts (JSON, CSV, Markdown)."""

    def export(
        self,
        project_id: str,
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
        markdown_report: str,
        output_dir: Optional[str] = None,
    ) -> Path:
        out = Path(output_dir) if output_dir else Path("output/manufacturing_agent")
        out.mkdir(parents=True, exist_ok=True)

        # 1. mfg_processes.json
        (out / "mfg_processes.json").write_text(
            json.dumps([p.model_dump() for p in processes], indent=2), encoding="utf-8"
        )

        # 2. dfm_findings.json
        (out / "dfm_findings.json").write_text(
            json.dumps([f.model_dump() for f in dfm_findings], indent=2), encoding="utf-8"
        )

        # 3. dfa_analysis.json
        (out / "dfa_analysis.json").write_text(
            json.dumps([m.model_dump() for m in dfa_models], indent=2), encoding="utf-8"
        )

        # 4. tolerances.json
        (out / "tolerances.json").write_text(
            json.dumps([t.model_dump() for t in tolerances], indent=2), encoding="utf-8"
        )

        # 5. tooling.json
        (out / "tooling.json").write_text(
            json.dumps([tl.model_dump() for tl in tooling], indent=2), encoding="utf-8"
        )

        # 6. inspections.json
        (out / "inspections.json").write_text(
            json.dumps([i.model_dump() for i in inspections], indent=2), encoding="utf-8"
        )

        # 7. mfg_recommendations.json
        (out / "mfg_recommendations.json").write_text(
            json.dumps([r.model_dump() for r in recommendations], indent=2), encoding="utf-8"
        )

        # 8. cost_drivers.json
        (out / "cost_drivers.json").write_text(
            json.dumps([c.model_dump() for c in cost_drivers], indent=2), encoding="utf-8"
        )

        # 9. mfg_report.md
        (out / "mfg_report.md").write_text(markdown_report, encoding="utf-8")

        # 10. mfg_findings.csv
        csv_path = out / "mfg_findings.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Finding ID", "Type", "Target", "Category", "Severity", "Description", "Evidence"])
            for f_item in dfm_findings:
                writer.writerow([f_item.finding_id, "DFM", f_item.component_id, f_item.category, f_item.severity, f_item.description, f_item.evidence_level])
            for m in dfa_models:
                for d_item in m.findings:
                    writer.writerow([d_item.finding_id, "DFA", m.assembly_id, d_item.category, d_item.severity, d_item.description, d_item.evidence_level])

        logger.info(f"Manufacturing deliverables exported to {out}")
        return out
