"""
File export service for EngineeringExecutionAgent (Section 62).
Exports the 7 required execution and audit JSON/Markdown artifacts.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from research_agents.engineering_execution_agent.schemas import EngineeringExecutionAgentOutput


class ExecutionFileExporter:
    """Safely exports Engineering Execution JSON and Markdown artifact bundles."""

    def export_artifacts(
        self,
        output: EngineeringExecutionAgentOutput,
        output_dir: str,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Generates:
        1. execution_result.json
        2. execution_report.md
        3. execution_graph.json
        4. audit_trail.json
        5. task_results.json
        6. changed_files.json
        7. authorization_events.json

        Returns:
            List of absolute paths to created files.
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        files_to_write: Dict[str, Any] = {
            "execution_result.json": output.model_dump(mode="json"),
            "execution_report.md": output.structured_report_markdown,
            "execution_graph.json": output.execution_graph.model_dump(mode="json"),
            "audit_trail.json": [a.model_dump(mode="json") for a in output.audit_trail],
            "task_results.json": {
                "completed": output.completed_tasks,
                "failed": output.failed_tasks,
                "blocked": output.blocked_tasks,
            },
            "changed_files.json": output.changed_files,
            "authorization_events.json": output.denied_actions,
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
