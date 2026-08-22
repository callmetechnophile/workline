"""Tests for project-scoped SurrealDB export, import, and transactional restoration."""

from pathlib import Path
import pytest

from backend.workline.git.repository import ProjectRepositoryManager
from backend.workline.project.export_service import ExportService
from backend.workline.project.import_service import ImportService
from backend.workline.project.models import ImportStrategy


def test_surrealdb_project_scoped_export(tmp_path: Path):
    """Test that SurrealDB export collects only project-scoped records."""
    proj = tmp_path / "rover-alpha"
    proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj, "rover-alpha", "Rover Alpha", project_version="0.1.0")

    exporter = ExportService()
    pkg_file, manifest, _ = exporter.export_project(proj, output_file=tmp_path / "alpha.wlipjt")

    assert manifest.surrealdb.schema_version == 1
    assert "component" in manifest.surrealdb.exported_tables
    assert "project" in manifest.surrealdb.exported_tables


def test_surrealdb_import_and_restoration(tmp_path: Path):
    """Test importing and restoring project state."""
    source_proj = tmp_path / "source-rover"
    source_proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(source_proj, "source-rover", "Source Rover", project_version="0.2.0")

    (source_proj / ".workline" / "pcb.wlpcb").write_text(
        '{"board": {"width": 120.0, "height": 90.0}, "components": [{"id": "U1", "mpn": "ESP32-S3"}], "nets": [{"name": "GND"}]}',
        encoding="utf-8",
    )

    exporter = ExportService()
    pkg_file, _, _ = exporter.export_project(source_proj, output_file=tmp_path / "source.wlipjt")

    importer = ImportService()
    dest_dir, restored_toon = importer.import_project(
        package_path=pkg_file,
        target_project_name="restored-rover",
        strategy=ImportStrategy.NEW_PROJECT,
        workspace_path=tmp_path / "workspace",
    )

    assert dest_dir.exists()
    assert (dest_dir / ".workline" / "pcb.wlpcb").exists()
    assert restored_toon.project_id == "restored-rover"
    assert restored_toon.project_version == "0.2.0"
