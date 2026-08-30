"""
File export service for VerificationQAAgent (Section 63).
Safely exports the 11 required JSON and Markdown verification artifacts.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from research_agents.verification_qa_agent.schemas import VerificationQAAgentOutput


class QAFileExporter:
    """Safely exports Engineering Verification & QA JSON and Markdown artifact bundles."""

    def export_artifacts(
        self,
        output: VerificationQAAgentOutput,
        output_dir: str,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Generates 11 files:
        1. verification_result.json
        2. verification_report.md
        3. requirement_matrix.json
        4. test_results.json
        5. coverage_matrix.json
        6. security_report.json
        7. architecture_conformance.json
        8. bom_conformance.json
        9. authorization_verification.json
        10. verification_traceability.json
        11. correction_report.json
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        files_to_write: Dict[str, Any] = {
            "verification_result.json": output.model_dump(mode="json"),
            "verification_report.md": output.structured_report_markdown,
            "requirement_matrix.json": [r.model_dump(mode="json") for r in output.requirements],
            "test_results.json": [t.model_dump(mode="json") for t in output.test_results],
            "coverage_matrix.json": {
                "requirements_passed": output.final_verdict.requirements_passed,
                "requirements_failed": output.final_verdict.requirements_failed,
                "requirements": [r.model_dump(mode="json") for r in output.requirements],
            },
            "security_report.json": [s.model_dump(mode="json") for s in output.security_findings],
            "architecture_conformance.json": output.architecture_conformance.model_dump(mode="json"),
            "bom_conformance.json": output.bom_conformance.model_dump(mode="json"),
            "authorization_verification.json": output.authorization_verification,
            "verification_traceability.json": [tr.model_dump(mode="json") for tr in output.traceability],
            "correction_report.json": [c.model_dump(mode="json") for c in output.corrections],
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
