"""
File export service for EngineeringSynthesisAgent (Section 36).
Exports the 5 required engineering synthesis artifacts safely without overwriting.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from research_agents.engineering_synthesis_agent.schemas import EngineeringSynthesisAgentOutput


class EngineeringFileExporter:
    """Safely exports synthesis JSON and Markdown artifact bundles."""

    def export_artifacts(
        self,
        output: EngineeringSynthesisAgentOutput,
        output_dir: str,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Generates:
        1. engineering_analysis.json
        2. engineering_report.md
        3. engineering_decisions.json
        4. engineering_risks.json
        5. engineering_validation.json

        Returns:
            List of absolute paths to created files.
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        files_to_write: Dict[str, Any] = {
            "engineering_analysis.json": output.model_dump(mode="json"),
            "engineering_report.md": output.structured_report_markdown,
            "engineering_decisions.json": [d.model_dump(mode="json") for d in output.decisions],
            "engineering_risks.json": [r.model_dump(mode="json") for r in output.risks],
            "engineering_validation.json": [v.model_dump(mode="json") for v in output.validation_requirements],
        }

        for filename, content in files_to_write.items():
            target_file = out_path / filename
            if target_file.exists() and not overwrite:
                logger.warning(f"File already exists and overwrite=False: {target_file}")
                continue

            if isinstance(content, str):
                target_file.write_text(content, encoding="utf-8")
            else:
                target_file.write_text(json.dumps(content, indent=2), encoding="utf-8")

            created_files.append(str(target_file))

        return created_files
