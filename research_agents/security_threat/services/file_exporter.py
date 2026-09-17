"""
File Exporter for Security Deliverables (Agent #22).
"""

import csv
import json
from pathlib import Path
from typing import List, Optional
from loguru import logger

from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    SecurityControl,
    SecurityDashboardData,
    SecurityTestCase,
    ThreatObject,
)


class FileExporter:
    """Exports security artifacts (security_assets.json, security_threats.json, attack_surface.json, attack_paths.json, security_controls.json, security_tests.json, security_report.md, security_threats.csv)."""

    def export(
        self,
        project_id: str,
        assets: List[AssetObject],
        attack_surface: List[AttackSurfaceEntry],
        threats: List[ThreatObject],
        attack_paths: List[AttackPath],
        controls: List[SecurityControl],
        security_tests: List[SecurityTestCase],
        dashboard: SecurityDashboardData,
        markdown_report: str,
        output_dir: Optional[str] = None,
    ) -> Path:
        out = Path(output_dir) if output_dir else Path("output/security_threat")
        out.mkdir(parents=True, exist_ok=True)

        # 1. security_assets.json
        (out / "security_assets.json").write_text(
            json.dumps([a.model_dump() for a in assets], indent=2), encoding="utf-8"
        )

        # 2. security_threats.json
        (out / "security_threats.json").write_text(
            json.dumps([t.model_dump() for t in threats], indent=2), encoding="utf-8"
        )

        # 3. attack_surface.json
        (out / "attack_surface.json").write_text(
            json.dumps([e.model_dump() for e in attack_surface], indent=2), encoding="utf-8"
        )

        # 4. attack_paths.json
        (out / "attack_paths.json").write_text(
            json.dumps([p.model_dump() for p in attack_paths], indent=2), encoding="utf-8"
        )

        # 5. security_controls.json
        (out / "security_controls.json").write_text(
            json.dumps([c.model_dump() for c in controls], indent=2), encoding="utf-8"
        )

        # 6. security_tests.json
        (out / "security_tests.json").write_text(
            json.dumps([st.model_dump() for st in security_tests], indent=2), encoding="utf-8"
        )

        # 7. security_report.md
        (out / "security_report.md").write_text(markdown_report, encoding="utf-8")

        # 8. security_threats.csv
        csv_path = out / "security_threats.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Threat ID", "Title", "Category", "Severity", "Likelihood", "Risk Score", "Status", "Is Critical"
            ])
            for t in threats:
                writer.writerow([
                    t.threat_id,
                    t.title,
                    t.category,
                    t.severity or "",
                    t.likelihood or "",
                    t.risk_score or "",
                    t.status,
                    t.is_critical,
                ])

        logger.info(f"Security threat deliverables exported to {out}")
        return out
