"""Tests for .wlipjt package creation, extraction, manifest, checksums, inspection, and corruption detection."""

import io
from pathlib import Path
import zipfile
import pytest

from backend.workline.git.repository import ProjectRepositoryManager
from backend.workline.project.errors import ChecksumMismatchError, CorruptedPackageError
from backend.workline.project.export_service import ExportService
from backend.workline.project.inspector import PackageInspector
from backend.workline.project.models import ExportOptions, PackageValidationStatus


@pytest.fixture
def sample_project_dir(tmp_path: Path) -> Path:
    """Fixture providing a populated Workline project directory."""
    proj = tmp_path / "telemetry-probe"
    proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj, "telemetry-probe", "Telemetry Probe", project_version="0.3.0")

    # Add requirements doc
    docs = proj / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "requirements.md").write_text("# Telemetry Requirements\nBudget: $5000", encoding="utf-8")

    # Add PCB state
    (proj / ".workline" / "pcb.wlpcb").write_text(
        '{"board": {"width": 80.0, "height": 60.0}, "components": [{"id": "U1", "mpn": "STM32F401"}], "nets": [{"name": "VCC"}]}',
        encoding="utf-8",
    )
    return proj


def test_package_creation_and_structure(sample_project_dir: Path, tmp_path: Path):
    """Test full package creation with all required internal TOON files and manifest."""
    exporter = ExportService()
    pkg_file, manifest, warnings = exporter.export_project(sample_project_dir, output_file=tmp_path / "probe.wlipjt")

    assert pkg_file.exists()
    assert pkg_file.suffix == ".wlipjt"
    assert manifest.project_id == "telemetry-probe"
    assert manifest.project_version == "0.3.0"
    assert manifest.format == "wlipjt"
    assert manifest.format_version == 1
    assert manifest.components_count == 1
    assert manifest.nets_count == 1

    # Inspect zip entries
    with zipfile.ZipFile(pkg_file, "r") as zf:
        namelist = set(zf.namelist())
        expected_entries = [
            "manifest.toon",
            "checksums.toon",
            "project/project.toon",
            "project/requirements.toon",
            "project/architecture.toon",
            "project/constraints.toon",
            "engineering/components.toon",
            "engineering/nets.toon",
            "engineering/bom.toon",
            "engineering/power.toon",
            "engineering/pcb.toon",
            "engineering/thermal.toon",
            "research/sources.toon",
            "research/findings.toon",
            "research/decisions.toon",
            "ai/agents.toon",
            "ai/workflows.toon",
            "ai/model_metadata.toon",
            "procurement/bom.toon",
            "procurement/suppliers.toon",
            "procurement/orders.toon",
            "versions/version.toon",
            "artifacts/metadata.toon",
            "git/metadata.toon",
            "team/metadata.toon",
        ]
        for exp in expected_entries:
            assert exp in namelist, f"Missing expected entry: {exp}"


def test_deterministic_serialization(sample_project_dir: Path, tmp_path: Path):
    """Test that identical project states produce identical byte outputs."""
    exporter = ExportService()
    pkg1, m1, _ = exporter.export_project(sample_project_dir, output_file=tmp_path / "pkg1.wlipjt")
    pkg2, m2, _ = exporter.export_project(sample_project_dir, output_file=tmp_path / "pkg2.wlipjt")

    # Verify identical normalized engineering states
    with zipfile.ZipFile(pkg1, "r") as z1, zipfile.ZipFile(pkg2, "r") as z2:
        assert z1.read("engineering/components.toon") == z2.read("engineering/components.toon")
        assert z1.read("engineering/nets.toon") == z2.read("engineering/nets.toon")
        assert z1.read("engineering/pcb.toon") == z2.read("engineering/pcb.toon")
        assert z1.read("project/constraints.toon") == z2.read("project/constraints.toon")

    assert m1.project_id == m2.project_id
    assert m1.components_count == m2.components_count


def test_read_only_package_inspection_and_verification(sample_project_dir: Path, tmp_path: Path):
    """Test read-only inspection returning statistics and valid integrity status."""
    exporter = ExportService()
    pkg_file, _, _ = exporter.export_project(sample_project_dir, output_file=tmp_path / "inspect_test.wlipjt")

    inspection = PackageInspector.inspect(pkg_file)
    assert inspection.valid is True
    assert inspection.integrity_status == "VALID"
    assert inspection.manifest.project_id == "telemetry-probe"
    assert inspection.manifest.project_version == "0.3.0"
    assert inspection.size_breakdown.total_package_size_bytes > 0

    is_valid, errors = PackageInspector.verify(pkg_file)
    assert is_valid is True
    assert len(errors) == 0


def test_corrupted_package_detection(sample_project_dir: Path, tmp_path: Path):
    """Test that modifying or tampering with an internal entry fails verification."""
    exporter = ExportService()
    pkg_file, _, _ = exporter.export_project(sample_project_dir, output_file=tmp_path / "tampered.wlipjt")

    # Read zip, tamper with an entry, rewrite
    entries = {}
    with zipfile.ZipFile(pkg_file, "r") as zf:
        for name in zf.namelist():
            entries[name] = zf.read(name)

    # Corrupt engineering/components.toon
    entries["engineering/components.toon"] = b"TAMPERED_CONTENT_MALICIOUS"

    tampered_file = tmp_path / "tampered_corrupt.wlipjt"
    with zipfile.ZipFile(tampered_file, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)

    is_valid, errors = PackageInspector.verify(tampered_file)
    assert is_valid is False
    assert any("Checksum mismatch" in e for e in errors)

    insp = PackageInspector.inspect(tampered_file)
    assert insp.valid is False
    assert insp.integrity_status == "CORRUPTED"
