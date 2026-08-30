"""
File export service for ComponentPlanningAgent (Section 46).
Safely exports the 7 required BOM JSON and Markdown artifacts.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from research_agents.component_planning_agent.schemas import ComponentPlanningAgentOutput


class BOMFileExporter:
    """Safely exports Bill of Materials JSON and Markdown artifact bundles."""

    def export_artifacts(
        self,
        output: ComponentPlanningAgentOutput,
        output_dir: str,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Generates:
        1. bom.json
        2. bom.md
        3. bom_items.json
        4. component_requirements.json
        5. component_alternatives.json
        6. bom_validation.json
        7. bom_traceability.json

        Returns:
            List of absolute paths to created files.
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        files_to_write: Dict[str, Any] = {
            "bom.json": output.model_dump(mode="json"),
            "bom.md": output.structured_bom_markdown,
            "bom_items.json": [item.model_dump(mode="json") for item in output.items],
            "component_requirements.json": [req.model_dump(mode="json") for req in output.component_requirements],
            "component_alternatives.json": [alt.model_dump(mode="json") for alt in output.alternatives],
            "bom_validation.json": [val.model_dump(mode="json") for val in output.validation_requirements],
            "bom_traceability.json": [tr.model_dump(mode="json") for tr in output.traceability],
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
