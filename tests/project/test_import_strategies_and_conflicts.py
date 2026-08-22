"""Tests for import strategies (NEW_PROJECT, RESTORE, MERGE), conflict detection, and migration."""

from pathlib import Path
import pytest

from backend.workline.git.repository import ProjectRepositoryManager
from backend.workline.project.errors import ProjectConflictError
from backend.workline.project.export_service import ExportService
from backend.workline.project.import_service import ImportService
from backend.workline.project.migrations.migrator import PackageMigrator
from backend.workline.project.models import ImportStrategy


@pytest.fixture
def exported_package(tmp_path: Path) -> Path:
    proj = tmp_path / "original-project"
    proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj, "original-project", "Original Project", project_version="0.1.0")

    exporter = ExportService()
    pkg_file, _, _ = exporter.export_project(proj, output_file=tmp_path / "orig.wlipjt")
    return pkg_file


def test_import_new_project_strategy(exported_package: Path, tmp_path: Path):
    """Test importing with NEW_PROJECT strategy creating a distinct project ID."""
    ws = tmp_path / "workspace"
    importer = ImportService()

    dest_dir, manifest = importer.import_project(
        package_path=exported_package,
        target_project_name="Cloned Rover",
        strategy=ImportStrategy.NEW_PROJECT,
        workspace_path=ws,
    )

    assert dest_dir.exists()
    assert dest_dir.name == "cloned-rover"
    assert manifest.project_id == "cloned-rover"
    assert manifest.project_name == "Cloned Rover"


def test_import_conflict_detection_and_protection(exported_package: Path, tmp_path: Path):
    """Test that importing an existing project ID with RESTORE raises ProjectConflictError unless overwrite is specified."""
    ws = tmp_path / "workspace"
    importer = ImportService()

    # First import
    importer.import_project(
        package_path=exported_package,
        target_project_name="original-project",
        strategy=ImportStrategy.RESTORE,
        workspace_path=ws,
    )

    # Second import without overwrite should fail with conflict
    with pytest.raises(ProjectConflictError) as exc_info:
        importer.import_project(
            package_path=exported_package,
            target_project_name="original-project",
            strategy=ImportStrategy.RESTORE,
            workspace_path=ws,
            overwrite=False,
        )
    assert "original-project" in str(exc_info.value)

    # With overwrite=True should succeed
    dest_dir2, _ = importer.import_project(
        package_path=exported_package,
        target_project_name="original-project",
        strategy=ImportStrategy.RESTORE,
        workspace_path=ws,
        overwrite=True,
    )
    assert dest_dir2.exists()


def test_package_format_migration():
    """Test PackageMigrator migrating v0/v1 manifest schemas."""
    assert PackageMigrator.can_migrate(1) is True
    assert PackageMigrator.can_migrate(2) is False

    old_manifest = {"format_version": 0, "project_id": "legacy-rover", "format": "wlipjt"}
    migrated, did_migrate = PackageMigrator.migrate_package_manifest(old_manifest)
    assert did_migrate is True
    assert migrated["format_version"] == 1
