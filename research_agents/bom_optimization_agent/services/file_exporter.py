"""
File export service for BOMOptimizationAgent (Section 47).
Safely exports the 7 required procurement JSON and Markdown artifacts.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from research_agents.bom_optimization_agent.schemas import BOMOptimizationAgentOutput


class ProcurementFileExporter:
    """Safely exports Procurement Optimization JSON and Markdown artifact bundles."""

    def export_artifacts(
        self,
        output: BOMOptimizationAgentOutput,
        output_dir: str,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Generates:
        1. procurement_optimization.json
        2. procurement_report.md
        3. optimized_bom.json
        4. supplier_comparison.json
        5. shipping_analysis.json
        6. procurement_strategies.json
        7. procurement_traceability.json

        Returns:
            List of absolute paths to created files.
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        files_to_write: Dict[str, Any] = {
            "procurement_optimization.json": output.model_dump(mode="json"),
            "procurement_report.md": output.structured_report_markdown,
            "optimized_bom.json": [item.model_dump(mode="json") for item in output.optimized_items],
            "supplier_comparison.json": output.supplier_summary,
            "shipping_analysis.json": [order.model_dump(mode="json") for order in output.orders],
            "procurement_strategies.json": [strat.model_dump(mode="json") for strat in output.strategies],
            "procurement_traceability.json": [tr.model_dump(mode="json") for tr in output.traceability],
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
