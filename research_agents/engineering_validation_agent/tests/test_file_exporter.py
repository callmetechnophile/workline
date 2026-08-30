"""
Unit tests for ValidationFileExporter service (Section 51).
"""

from pathlib import Path
import tempfile
from research_agents.engineering_validation_agent.schemas import (
    EngineeringValidationAgentOutput,
    FinalVerdict,
    RequirementValidationItem,
    ValidationItem,
)
from research_agents.engineering_validation_agent.services.file_exporter import ValidationFileExporter


def test_file_export_creates_10_artifacts():
    exporter = ValidationFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = EngineeringValidationAgentOutput(
            project_id="proj_test_01",
            validation_id="VAL-001",
            verdict="READY",
            final_verdict=FinalVerdict(verdict="READY"),
            requirement_results=[
                RequirementValidationItem(requirement_id="REQ-01", description="Thermal detection")
            ],
            electrical_results=[
                ValidationItem(validation_id="VAL-E-01", category="electrical", title="Voltage", description="Passed")
            ],
            structured_report_markdown="# Engineering Design Verification Report",
        )

        files = exporter.export_artifacts(output, tmp_dir, overwrite=True)
        assert len(files) == 10

        dir_p = Path(tmp_dir)
        assert (dir_p / "validation.json").exists()
        assert (dir_p / "validation_report.md").exists()
        assert (dir_p / "validation_rules.json").exists()
        assert (dir_p / "requirement_validation.json").exists()
        assert (dir_p / "electrical_validation.json").exists()
        assert (dir_p / "power_validation.json").exists()
        assert (dir_p / "interface_validation.json").exists()
        assert (dir_p / "bom_validation.json").exists()
        assert (dir_p / "procurement_validation.json").exists()
        assert (dir_p / "validation_traceability.json").exists()


def test_file_export_prevents_overwrite_without_flag():
    exporter = ValidationFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = EngineeringValidationAgentOutput(
            project_id="proj_test_01",
            structured_report_markdown="Original Content",
        )

        exporter.export_artifacts(output, tmp_dir, overwrite=True)
        report_file = Path(tmp_dir) / "validation_report.md"
        assert report_file.read_text(encoding="utf-8") == "Original Content"

        output.structured_report_markdown = "Modified Content"
        exporter.export_artifacts(output, tmp_dir, overwrite=False)
        assert report_file.read_text(encoding="utf-8") == "Original Content"
