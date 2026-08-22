"""Tests for package diffing, timestamped backups, and release/snapshot integration."""

from pathlib import Path
import pytest

from backend.workline.git.repository import ProjectRepositoryManager
from backend.workline.project.backup import BackupService
from backend.workline.project.export_service import ExportService
from backend.workline.project.inspector import PackageInspector
from backend.workline.project.models import ExportOptions


def test_package_diff_computation(tmp_path: Path):
    """Test comparing two .wlipjt packages and reporting component and net differences."""
    mgr = ProjectRepositoryManager()
    exporter = ExportService()

    # Project A
    proj_a = tmp_path / "rover-v1"
    proj_a.mkdir(parents=True)
    mgr.init_project_git(proj_a, "rover", "Rover", project_version="0.1.0")
    (proj_a / ".workline" / "pcb.wlpcb").write_text(
        '{"board": {}, "components": [{"id": "U1", "mpn": "MCU1"}], "nets": [{"name": "VCC"}]}',
        encoding="utf-8",
    )
    pkg_a, _, _ = exporter.export_project(proj_a, output_file=tmp_path / "rover_v1.wlipjt")

    # Project B (added components & nets, bumped version)
    proj_b = tmp_path / "rover-v2"
    proj_b.mkdir(parents=True)
    mgr.init_project_git(proj_b, "rover", "Rover", project_version="0.2.0")
    (proj_b / ".workline" / "pcb.wlpcb").write_text(
        '{"board": {}, "components": [{"id": "U1", "mpn": "MCU1"}, {"id": "U2", "mpn": "SENSOR1"}], "nets": [{"name": "VCC"}, {"name": "SDA"}]}',
        encoding="utf-8",
    )
    pkg_b, _, _ = exporter.export_project(proj_b, output_file=tmp_path / "rover_v2.wlipjt")

    diff = PackageInspector.diff(pkg_a, pkg_b)
    assert diff.version_diff == "0.1.0 → 0.2.0"
    assert diff.components_added == 1
    assert diff.nets_added == 1


def test_timestamped_project_backup(tmp_path: Path):
    """Test creating a non-destructive timestamped package backup in project-backups/."""
    proj = tmp_path / "flight-control"
    proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj, "flight-control", "Flight Control", project_version="1.0.0")

    backup_svc = BackupService()
    backup_dir = tmp_path / "backups"
    pkg_file, manifest, _ = backup_svc.create_backup(proj, backup_dir=backup_dir)

    assert pkg_file.exists()
    assert pkg_file.parent == backup_dir
    assert "flight-control-" in pkg_file.name
    assert manifest.project_id == "flight-control"
