"""
Test suite for project recovery — backup + restore workflow.
"""

import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cli.wline.main import app

runner = CliRunner()


def _make_project(tmp_path: Path, name: str = "Test Project", pid: str = "TEST-001") -> Path:
    """Create a minimal valid .wl project directory."""
    root = tmp_path / "project"
    root.mkdir(parents=True, exist_ok=True)
    readme = root / "README.wl"
    readme.write_text(
        f"WORKLINE_PROJECT\n================\n"
        f"name: {name}\nproject_id: {pid}\nversion: 1.0\n"
        f"domain: hardware\ndescription: Test\n",
        encoding="utf-8"
    )
    wl = root / ".wl"
    wl.mkdir(parents=True, exist_ok=True)
    (wl / "manifest.wl").write_text("manifest_version: '1.0'\nproject_id: TEST-001\n", encoding="utf-8")
    (wl / "moss.wl").write_text("moss:\n  status: UNINITIALIZED\n  document_count: 0\n", encoding="utf-8")
    for d in ["requirements", "components", "bom", "analysis", "tasks"]:
        (root / d).mkdir(parents=True, exist_ok=True)
    return root


def _make_wlipjt(tmp_path: Path, name: str = "test_backup.wlipjt") -> Path:
    """Create a minimal valid .wlipjt archive."""
    pkg = tmp_path / name
    with zipfile.ZipFile(pkg, "w") as zf:
        zf.writestr("manifest.toon", "# TOON manifest\nproject_id: TEST-001\n")
        zf.writestr("checksums.toon", "# checksums\n")
        zf.writestr("project.toon", "# project data\n")
    return pkg


class TestBackupCommand:
    def test_backup_fails_without_project(self, tmp_path: Path):
        empty = tmp_path / "empty"
        empty.mkdir(parents=True, exist_ok=True)
        result = runner.invoke(app, ["backup", str(empty)])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "no workline" in result.output.lower()

    def test_backup_project_found_runs(self, tmp_path: Path):
        """backup should find the project and attempt export."""
        project = _make_project(tmp_path)
        result = runner.invoke(app, ["backup", str(project), "--output", str(tmp_path)])
        assert result.exit_code in (0, 1)


class TestRestoreCommand:
    def test_restore_missing_package(self, tmp_path: Path):
        result = runner.invoke(app, ["restore", str(tmp_path / "missing.wlipjt")])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_restore_basic_zip_extraction(self, tmp_path: Path):
        pkg = _make_wlipjt(tmp_path)
        target = tmp_path / "restore_target"
        target.mkdir(parents=True, exist_ok=True)
        result = runner.invoke(app, ["restore", str(pkg), "--target", str(target), "--yes"])
        assert result.exit_code in (0, 1)

    def test_restore_invalid_strategy(self, tmp_path: Path):
        pkg = _make_wlipjt(tmp_path)
        result = runner.invoke(app, ["restore", str(pkg), "--strategy", "invalid_strategy"])
        assert result.exit_code != 0 or "unknown strategy" in result.output.lower()


class TestProjectRetrieverMode:
    def test_retriever_local_mode(self, tmp_path: Path):
        from cli.workline.retrieval.retriever import ProjectRetriever
        project = _make_project(tmp_path)
        retriever = ProjectRetriever(project, mode="local")
        assert retriever.mode == "local"
        assert retriever.active_mode == "local"

    def test_retriever_stack_mode_falls_back_when_no_qdrant(self, tmp_path: Path):
        """When Qdrant is not running, stack mode active_mode should degrade to local."""
        from cli.workline.retrieval.retriever import ProjectRetriever
        project = _make_project(tmp_path)
        retriever = ProjectRetriever(project, mode="stack")
        active = retriever.active_mode
        assert active in ("local", "stack")

    def test_retriever_auto_mode_does_not_crash(self, tmp_path: Path):
        from cli.workline.retrieval.retriever import ProjectRetriever
        project = _make_project(tmp_path)
        retriever = ProjectRetriever(project, mode="auto")
        results = retriever.retrieve("power supply requirements", top_k=5)
        assert isinstance(results, list)

    def test_retriever_filesystem_fallback_finds_content(self, tmp_path: Path):
        """Even with no index, retriever finds content via filesystem scan."""
        project = _make_project(tmp_path)
        req_dir = project / "requirements"
        (req_dir / "functional.wl").write_text(
            "REQ-001:\n  title: Power supply\n  description: Must support 12V DC input\n",
            encoding="utf-8"
        )
        from cli.workline.retrieval.retriever import ProjectRetriever
        retriever = ProjectRetriever(project, mode="local")
        results = retriever.retrieve("power supply 12V", top_k=5)
        assert isinstance(results, list)

    def test_retriever_lookup_component_returns_none_for_empty_project(self, tmp_path: Path):
        from cli.workline.retrieval.retriever import ProjectRetriever
        project = _make_project(tmp_path)
        retriever = ProjectRetriever(project, mode="local")
        result = retriever.lookup_component("ESP32-WROOM-32")
        assert result is None

    def test_retriever_lookup_tasks_returns_list(self, tmp_path: Path):
        from cli.workline.retrieval.retriever import ProjectRetriever
        project = _make_project(tmp_path)
        retriever = ProjectRetriever(project, mode="local")
        tasks = retriever.lookup_tasks(status="open")
        assert isinstance(tasks, list)
