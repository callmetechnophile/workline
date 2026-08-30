"""
Unit tests for ArchitectureFileExporter service (Section 45).
"""

from pathlib import Path
import tempfile
from research_agents.engineering_architecture_agent.schemas import (
    ArchitectureMeta,
    EngineeringArchitectureAgentOutput,
    InterfaceItem,
    PowerDomainItem,
    ProjectMeta,
    SubsystemItem,
)
from research_agents.engineering_architecture_agent.services.file_exporter import ArchitectureFileExporter


def test_file_export_creates_8_artifacts():
    exporter = ArchitectureFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = EngineeringArchitectureAgentOutput(
            project=ProjectMeta(title="Export Test Drone"),
            architecture=ArchitectureMeta(architecture_id="ARCH-01", architecture_name="Test Arch", description="Desc", architecture_type="Type"),
            subsystems=[SubsystemItem(subsystem_id="SUB-01", name="Compute", purpose="AI")],
            interfaces=[InterfaceItem(interface_id="IF-01", source="A", target="B", interface_type="SPI", purpose="Video")],
            power_domains=[PowerDomainItem(power_domain_id="PWR-01", name="5V Rail", source="Buck", voltage="5V", regulation="Buck", protection=[])],
            structured_report_markdown="# System Architecture Report",
        )

        files = exporter.export_artifacts(output, tmp_dir, overwrite=True)
        assert len(files) == 8

        # Check all 8 file names exist
        dir_p = Path(tmp_dir)
        assert (dir_p / "architecture.json").exists()
        assert (dir_p / "architecture.md").exists()
        assert (dir_p / "architecture_graph.json").exists()
        assert (dir_p / "block_diagram.json").exists()
        assert (dir_p / "subsystems.json").exists()
        assert (dir_p / "interfaces.json").exists()
        assert (dir_p / "power_architecture.json").exists()
        assert (dir_p / "validation_requirements.json").exists()


def test_file_export_prevents_overwrite_without_flag():
    exporter = ArchitectureFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = EngineeringArchitectureAgentOutput(
            project=ProjectMeta(title="Export Test Drone"),
            architecture=ArchitectureMeta(architecture_id="ARCH-01", architecture_name="Test Arch", description="Desc", architecture_type="Type"),
            structured_report_markdown="Original Content",
        )

        exporter.export_artifacts(output, tmp_dir, overwrite=True)
        report_file = Path(tmp_dir) / "architecture.md"
        assert report_file.read_text(encoding="utf-8") == "Original Content"

        # Attempt export with overwrite=False
        output.structured_report_markdown = "Modified Content"
        exporter.export_artifacts(output, tmp_dir, overwrite=False)
        assert report_file.read_text(encoding="utf-8") == "Original Content"
