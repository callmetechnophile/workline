"""
Unit tests for EngineeringFileExporter service (Section 36).
"""

from pathlib import Path
import tempfile
from research_agents.engineering_synthesis_agent.schemas import (
    EngineeringDecision,
    EngineeringRisk,
    EngineeringSynthesisAgentOutput,
    ProjectMeta,
    ValidationRequirement,
)
from research_agents.engineering_synthesis_agent.services.file_exporter import EngineeringFileExporter


def test_file_export_creates_5_artifacts():
    exporter = EngineeringFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = EngineeringSynthesisAgentOutput(
            project=ProjectMeta(title="Export Test Drone"),
            decisions=[EngineeringDecision(decision_id="DEC-01", decision_area="Compute", selected_option="Jetson", decision_reason="Reason")],
            risks=[EngineeringRisk(risk_id="RISK-01", category="thermal", description="Risk", mitigation="Mitigation")],
            validation_requirements=[ValidationRequirement(validation_id="VAL-01", category="bench_test", description="Val", acceptance_criteria="OK")],
            structured_report_markdown="# Test Report",
        )

        files = exporter.export_artifacts(output, tmp_dir, overwrite=True)
        assert len(files) == 5

        # Check file names exist
        dir_p = Path(tmp_dir)
        assert (dir_p / "engineering_analysis.json").exists()
        assert (dir_p / "engineering_report.md").exists()
        assert (dir_p / "engineering_decisions.json").exists()
        assert (dir_p / "engineering_risks.json").exists()
        assert (dir_p / "engineering_validation.json").exists()


def test_file_export_prevents_overwrite_without_flag():
    exporter = EngineeringFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = EngineeringSynthesisAgentOutput(
            project=ProjectMeta(title="Export Test Drone"),
            structured_report_markdown="Original Content",
        )

        exporter.export_artifacts(output, tmp_dir, overwrite=True)
        report_file = Path(tmp_dir) / "engineering_report.md"
        assert report_file.read_text(encoding="utf-8") == "Original Content"

        # Attempt export with overwrite=False
        output.structured_report_markdown = "Modified Content"
        exporter.export_artifacts(output, tmp_dir, overwrite=False)
        assert report_file.read_text(encoding="utf-8") == "Original Content"
