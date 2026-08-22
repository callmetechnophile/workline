"""Tests for project Git repository management, TOON manifest, snapshots, and releases."""

from pathlib import Path
import pytest

from backend.workline.git.models import (
    ProjectGitHubManifest,
    ProjectGitManifest,
    WorklineToonManifest,
)
from backend.workline.git.repository import ProjectRepositoryManager
from backend.workline.git.service import GitService
from backend.workline.git.toon import ToonSerializer


def test_toon_serializer_roundtrip():
    """Test encoding and decoding of project manifest in canonical TOON format."""
    manifest = WorklineToonManifest(
        project_id="autonomous-rover",
        project_name="Autonomous Rover",
        workline_version="0.1.0",
        schema_version=1,
        project_version="0.3.0",
        git=ProjectGitManifest(
            initialized=True,
            current_branch="main",
            current_commit="8f23a91b4c5d",
        ),
        github=ProjectGitHubManifest(
            connected=True,
            owner="acme-robotics",
            repository="autonomous-rover",
            remote="https://github.com/acme-robotics/autonomous-rover.git",
        ),
    )

    encoded = ToonSerializer.manifest_to_toon(manifest)
    assert "project_id: autonomous-rover" in encoded
    assert "schema_version: 1" in encoded
    assert "project_version: 0.3.0" in encoded
    assert "connected: true" in encoded

    decoded = ToonSerializer.manifest_from_toon(encoded)
    assert decoded.project_id == "autonomous-rover"
    assert decoded.project_version == "0.3.0"
    assert decoded.schema_version == 1
    assert decoded.git.current_branch == "main"
    assert decoded.git.current_commit == "8f23a91b4c5d"
    assert decoded.github.connected is True
    assert decoded.github.owner == "acme-robotics"


def test_project_git_initialization(tmp_path: Path):
    """Test full project Git initialization: git repo, .gitignore, .workline/project.toon, and initial commit."""
    mgr = ProjectRepositoryManager()

    repo = mgr.init_project_git(
        project_path=tmp_path,
        project_id="solar-drone",
        project_name="Solar Drone",
        default_branch="main",
        project_version="0.1.0",
        schema_version=1,
    )

    assert repo.project_id == "solar-drone"
    assert repo.default_branch == "main"
    assert repo.current_commit is not None

    # Verify .gitignore
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    assert ".env" in gitignore.read_text(encoding="utf-8")

    # Verify .workline/project.toon
    toon_path = tmp_path / ".workline" / "project.toon"
    assert toon_path.exists()

    manifest = mgr.load_toon_manifest(tmp_path)
    assert manifest is not None
    assert manifest.project_id == "solar-drone"
    assert manifest.project_name == "Solar Drone"
    assert manifest.project_version == "0.1.0"
    assert manifest.schema_version == 1
    assert manifest.git.initialized is True
    assert manifest.git.current_commit == repo.current_commit


def test_version_distinction(tmp_path: Path):
    """Verify that Project Version (semver) is strictly distinct from Git Commit Hash."""
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(tmp_path, "rover-v2", "Rover V2", project_version="0.2.1", schema_version=2)

    manifest = mgr.load_toon_manifest(tmp_path)
    assert manifest.project_version == "0.2.1"
    assert manifest.schema_version == 2
    assert manifest.git.current_commit != manifest.project_version


def test_deterministic_project_snapshot(tmp_path: Path):
    """Test creating a deterministic project state snapshot linked to Git commit."""
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(tmp_path, "telemetry-unit", "Telemetry Unit", project_version="1.0.0")

    snapshot = mgr.create_snapshot(tmp_path)
    assert snapshot.snapshot_id.startswith("snap_")
    assert snapshot.project_id == "telemetry-unit"
    assert snapshot.project_version == "1.0.0"
    assert snapshot.schema_version == 1
    assert snapshot.git_commit is not None
    assert "branch" in snapshot.data_summary


def test_formal_project_release_workflow(tmp_path: Path):
    """Test release workflow: bump project version, create release commit, and tag Git repository."""
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(tmp_path, "smart-hub", "Smart Hub", project_version="0.1.0")

    rel_info = mgr.create_release(
        project_path=tmp_path,
        release_version="0.2.0",
        tag_message="Release version 0.2.0 with enhanced motor control",
    )

    assert rel_info["project_id"] == "smart-hub"
    assert rel_info["previous_version"] == "0.1.0"
    assert rel_info["release_version"] == "0.2.0"
    assert rel_info["git_tag"] == "v0.2.0"
    assert rel_info["commit_hash"] is not None

    # Verify manifest updated
    manifest = mgr.load_toon_manifest(tmp_path)
    assert manifest.project_version == "0.2.0"

    # Verify Git tag exists
    git = GitService()
    tags = git.list_tags(tmp_path)
    assert any(t.name == "v0.2.0" for t in tags)
