"""
File export service for EngineeringArchitectureAgent (Section 45).
Exports the 8 required architecture JSON and Markdown artifacts safely.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from research_agents.engineering_architecture_agent.schemas import EngineeringArchitectureAgentOutput


class ArchitectureFileExporter:
    """Safely exports architecture JSON and Markdown artifact bundles."""

    def export_artifacts(
        self,
        output: EngineeringArchitectureAgentOutput,
        output_dir: str,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Generates:
        1. architecture.json
        2. architecture.md
        3. architecture_graph.json
        4. block_diagram.json
        5. subsystems.json
        6. interfaces.json
        7. power_architecture.json
        8. validation_requirements.json

        Returns:
            List of absolute paths to created files.
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        files_to_write: Dict[str, Any] = {
            "architecture.json": output.model_dump(mode="json"),
            "architecture.md": output.structured_report_markdown,
            "architecture_graph.json": output.architecture_graph.model_dump(mode="json"),
            "block_diagram.json": output.block_diagram.model_dump(mode="json"),
            "subsystems.json": [s.model_dump(mode="json") for s in output.subsystems],
            "interfaces.json": [i.model_dump(mode="json") for i in output.interfaces],
            "power_architecture.json": [p.model_dump(mode="json") for p in output.power_domains],
            "validation_requirements.json": [v.model_dump(mode="json") for v in output.validation_requirements],
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
