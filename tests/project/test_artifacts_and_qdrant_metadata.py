"""Tests for artifact payload handling and Qdrant vector metadata packaging."""

from pathlib import Path
import zipfile
import pytest

from backend.workline.git.repository import ProjectRepositoryManager
from backend.workline.project.export_service import ExportService
from backend.workline.project.import_service import ImportService
from backend.workline.project.inspector import PackageInspector
from backend.workline.project.models import ExportOptions, ImportStrategy


def test_artifact_modes_metadata_only_vs_included(tmp_path: Path):
    """Test that default export is METADATA_ONLY and --include-artifacts includes files."""
    proj = tmp_path / "drone-ai"
    proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj, "drone-ai", "Drone AI", project_version="1.0.0")

    # Create dummy artifact files
    art_dir = proj / "artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)
    (art_dir / "pinn_model.pt").write_bytes(b"PYTORCH_MODEL_WEIGHTS_DATA_SIMULATED_123456")
    (art_dir / "report.pdf").write_bytes(b"PDF_DOC_SIMULATED")

    exporter = ExportService()

    # 1. Default (Metadata only)
    pkg_meta, manifest_meta, _ = exporter.export_project(
        proj,
        output_file=tmp_path / "meta_only.wlipjt",
        options=ExportOptions(include_artifacts=False),
    )
    assert manifest_meta.artifacts_count == 2
    with zipfile.ZipFile(pkg_meta, "r") as zf:
        namelist = zf.namelist()
        assert "artifacts/metadata.toon" in namelist
        assert "artifacts/files/pinn_model.pt" not in namelist

    # 2. Included artifacts
    pkg_inc, manifest_inc, _ = exporter.export_project(
        proj,
        output_file=tmp_path / "included.wlipjt",
        options=ExportOptions(include_artifacts=True),
    )
    assert manifest_inc.artifacts_count == 2
    with zipfile.ZipFile(pkg_inc, "r") as zf:
        namelist = zf.namelist()
        assert "artifacts/metadata.toon" in namelist
        assert "artifacts/files/pinn_model.pt" in namelist
        assert "artifacts/files/report.pdf" in namelist


def test_artifact_import_restoration(tmp_path: Path):
    """Test that importing a package with included artifacts restores them to disk."""
    proj = tmp_path / "thermal-sim"
    proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj, "thermal-sim", "Thermal Sim")

    art_dir = proj / "artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)
    (art_dir / "weights.onnx").write_bytes(b"ONNX_WEIGHTS_BUFFER")

    exporter = ExportService()
    pkg_file, _, _ = exporter.export_project(
        proj,
        output_file=tmp_path / "thermal.wlipjt",
        options=ExportOptions(include_artifacts=True),
    )

    importer = ImportService()
    dest_dir, _ = importer.import_project(
        package_path=pkg_file,
        target_project_name="restored-thermal",
        strategy=ImportStrategy.NEW_PROJECT,
        workspace_path=tmp_path / "ws",
    )

    restored_art = dest_dir / "artifacts" / "weights.onnx"
    assert restored_art.exists()
    assert restored_art.read_bytes() == b"ONNX_WEIGHTS_BUFFER"


def test_qdrant_vector_metadata_exclusion(tmp_path: Path):
    """Test that Qdrant metadata includes collections/models but excludes raw float embeddings by default."""
    proj = tmp_path / "rag-system"
    proj.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj, "rag-system", "RAG System")

    exporter = ExportService()
    pkg_file, manifest, _ = exporter.export_project(
        proj,
        output_file=tmp_path / "rag.wlipjt",
        options=ExportOptions(include_vectors=False),
    )

    assert manifest.qdrant.included_vectors is False
    assert manifest.qdrant.embedding_model == "text-embedding-3-small"
    assert "workline_rag-system" in manifest.qdrant.collections
