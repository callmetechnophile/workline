"""
Unit tests for BOMFileExporter service (Section 46).
"""

from pathlib import Path
import tempfile
from research_agents.component_planning_agent.schemas import (
    BOMItem,
    BOMSummary,
    ComponentAlternativeItem,
    ComponentPlanningAgentOutput,
    ComponentRequirementItem,
)
from research_agents.component_planning_agent.services.file_exporter import BOMFileExporter


def test_file_export_creates_7_artifacts():
    exporter = BOMFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = ComponentPlanningAgentOutput(
            bom_id="BOM-001",
            project_id="proj_test_01",
            summary=BOMSummary(total_line_items=1),
            items=[
                BOMItem(
                    bom_item_id="BOM-001",
                    category="SBC",
                    part_number="Jetson",
                    manufacturer="NVIDIA",
                    component_name="Jetson",
                    description="AI",
                    subsystem_id="SUB-001",
                    role="compute",
                    selection_reason="AI",
                )
            ],
            component_requirements=[
                ComponentRequirementItem(
                    requirement_id="REQ-01",
                    category="SBC",
                    quantity=1,
                    required_specifications={},
                    source_subsystem="SUB-001",
                    reason="AI",
                )
            ],
            alternatives=[
                ComponentAlternativeItem(
                    alternative_id="ALT-01",
                    part_number="SC1111",
                    manufacturer="RPi",
                    compatibility="architecture_alternative",
                    reason="Low cost",
                )
            ],
            structured_bom_markdown="# Engineering Bill of Materials",
        )

        files = exporter.export_artifacts(output, tmp_dir, overwrite=True)
        assert len(files) == 7

        dir_p = Path(tmp_dir)
        assert (dir_p / "bom.json").exists()
        assert (dir_p / "bom.md").exists()
        assert (dir_p / "bom_items.json").exists()
        assert (dir_p / "component_requirements.json").exists()
        assert (dir_p / "component_alternatives.json").exists()
        assert (dir_p / "bom_validation.json").exists()
        assert (dir_p / "bom_traceability.json").exists()


def test_file_export_prevents_overwrite_without_flag():
    exporter = BOMFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = ComponentPlanningAgentOutput(
            bom_id="BOM-001",
            project_id="proj_test_01",
            structured_bom_markdown="Original Content",
        )

        exporter.export_artifacts(output, tmp_dir, overwrite=True)
        report_file = Path(tmp_dir) / "bom.md"
        assert report_file.read_text(encoding="utf-8") == "Original Content"

        output.structured_bom_markdown = "Modified Content"
        exporter.export_artifacts(output, tmp_dir, overwrite=False)
        assert report_file.read_text(encoding="utf-8") == "Original Content"
