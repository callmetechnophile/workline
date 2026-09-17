"""File exporter for Implementation Plan JSON and Markdown artifacts (Agent #10)."""
import json
from pathlib import Path
from typing import Optional
from loguru import logger
from research_agents.project_execution_agent.schemas import ImplementationPlan

class FileExporter:
    """Exports Implementation Plan artifacts to disk."""

    def export(self, plan: ImplementationPlan, markdown_report: str, output_dir: Optional[str] = None) -> Path:
        out = Path(output_dir) if output_dir else Path("output/implementation_plan")
        out.mkdir(parents=True, exist_ok=True)
        json_file = out / f"{plan.plan_id}.json"
        md_file = out / f"{plan.plan_id}_report.md"
        json_file.write_text(json.dumps(plan.model_dump(), indent=2), encoding="utf-8")
        md_file.write_text(markdown_report, encoding="utf-8")
        logger.info(f"Implementation Plan exported to {out}")
        return out
