"""
Unit tests for QAFileExporter service (Section 63).
"""

from pathlib import Path
import tempfile
from research_agents.verification_qa_agent.schemas import (
    FinalQAVerdict,
    VerificationQAAgentOutput,
)
from research_agents.verification_qa_agent.services.file_exporter import QAFileExporter


def test_qa_file_exporter_creates_11_artifacts():
    exporter = QAFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = VerificationQAAgentOutput(
            status="success",
            verification_id="QA-001",
            project_id="proj_01",
            verdict="VERIFIED",
            final_verdict=FinalQAVerdict(verdict="VERIFIED"),
            structured_report_markdown="# QA Report",
        )

        files = exporter.export_artifacts(output, tmp_dir, overwrite=True)
        assert len(files) == 11

        dir_p = Path(tmp_dir)
        assert (dir_p / "verification_result.json").exists()
        assert (dir_p / "verification_report.md").exists()
        assert (dir_p / "requirement_matrix.json").exists()
        assert (dir_p / "test_results.json").exists()
        assert (dir_p / "coverage_matrix.json").exists()
        assert (dir_p / "security_report.json").exists()
        assert (dir_p / "architecture_conformance.json").exists()
        assert (dir_p / "bom_conformance.json").exists()
        assert (dir_p / "authorization_verification.json").exists()
        assert (dir_p / "verification_traceability.json").exists()
        assert (dir_p / "correction_report.json").exists()
