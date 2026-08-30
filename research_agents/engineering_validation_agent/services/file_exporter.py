"""
File export service for EngineeringValidationAgent (Section 51).
Safely exports the 10 required validation JSON and Markdown artifacts.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from research_agents.engineering_validation_agent.schemas import EngineeringValidationAgentOutput


class ValidationFileExporter:
    """Safely exports Engineering Validation JSON and Markdown artifact bundles."""

    def export_artifacts(
        self,
        output: EngineeringValidationAgentOutput,
        output_dir: str,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Generates:
        1. validation.json
        2. validation_report.md
        3. validation_rules.json
        4. requirement_validation.json
        5. electrical_validation.json
        6. power_validation.json
        7. interface_validation.json
        8. bom_validation.json
        9. procurement_validation.json
        10. validation_traceability.json

        Returns:
            List of absolute paths to created files.
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        files_to_write: Dict[str, Any] = {
            "validation.json": output.model_dump(mode="json"),
            "validation_report.md": output.structured_report_markdown,
            "validation_rules.json": [r.model_dump(mode="json") for r in output.rule_results],
            "requirement_validation.json": [req.model_dump(mode="json") for req in output.requirement_results],
            "electrical_validation.json": [e.model_dump(mode="json") for e in output.electrical_results],
            "power_validation.json": [p.model_dump(mode="json") for p in output.power_results],
            "interface_validation.json": [i.model_dump(mode="json") for i in output.interface_results],
            "bom_validation.json": [b.model_dump(mode="json") for b in output.bom_results],
            "procurement_validation.json": [pr.model_dump(mode="json") for pr in output.procurement_results],
            "validation_traceability.json": [tr.model_dump(mode="json") for tr in output.traceability],
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
