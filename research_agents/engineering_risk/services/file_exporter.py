"""
File Exporter for JSON, CSV, and Markdown Deliverables (Agent #21).
"""

import csv
import io
import json
from pathlib import Path
from typing import List, Optional
from loguru import logger

from research_agents.engineering_risk.schemas import (
    FMEARecord,
    RiskDashboardData,
    RiskMitigation,
    RiskObject,
)


class FileExporter:
    """Exports risk artifacts (risk_register.json, fmea.json, risk_dashboard.json, risk_report.md, risk_register.csv)."""

    def export(
        self,
        project_id: str,
        risks: List[RiskObject],
        fmea_records: List[FMEARecord],
        mitigations: List[RiskMitigation],
        dashboard: RiskDashboardData,
        markdown_report: str,
        output_dir: Optional[str] = None,
    ) -> Path:
        out = Path(output_dir) if output_dir else Path("output/engineering_risk")
        out.mkdir(parents=True, exist_ok=True)

        # 1. risk_register.json
        (out / "risk_register.json").write_text(
            json.dumps([r.model_dump() for r in risks], indent=2), encoding="utf-8"
        )

        # 2. fmea.json
        (out / "fmea.json").write_text(
            json.dumps([f.model_dump() for f in fmea_records], indent=2), encoding="utf-8"
        )

        # 3. risk_dashboard.json
        (out / "risk_dashboard.json").write_text(
            json.dumps(dashboard.model_dump(), indent=2), encoding="utf-8"
        )

        # 4. risk_report.md
        (out / "risk_report.md").write_text(markdown_report, encoding="utf-8")

        # 5. risk_register.csv
        csv_path = out / "risk_register.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Risk ID", "Title", "Category", "Severity", "Likelihood", "Detectability", "RPN", "Level", "Status", "Single Point Failure"
            ])
            for r in risks:
                writer.writerow([
                    r.risk_id,
                    r.title,
                    r.category,
                    r.severity or "",
                    r.likelihood or "",
                    r.detectability or "",
                    r.risk_score or "",
                    r.risk_level,
                    r.status,
                    r.is_single_point_failure,
                ])

        logger.info(f"Engineering Risk deliverables exported to {out}")
        return out
