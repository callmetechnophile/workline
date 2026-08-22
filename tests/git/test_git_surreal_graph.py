"""Tests for SurrealDB Git graph metadata persistence and relationship edges."""

import pytest

from backend.workline.git.graph import GitGraphRepository
from backend.workline.git.models import (
    GitHubRepository,
    GitRepository,
    ProjectSnapshot,
    RepositoryVisibility,
)


@pytest.mark.anyio
async def test_git_graph_repository_persistence():
    """Test saving GitRepository metadata and linking Project -> GitRepository."""
    graph = GitGraphRepository()

    repo = GitRepository(
        repository_id="git_repo:autonomous-rover",
        project_id="autonomous-rover",
        local_path="/workspace/autonomous-rover",
        default_branch="main",
        current_branch="main",
        current_commit="abcdef123456",
        remote_url="https://github.com/acme/autonomous-rover.git",
        visibility=RepositoryVisibility.PRIVATE,
    )

    model = await graph.save_git_repository(repo)
    assert model.project_id == "autonomous-rover"
    assert model.current_commit == "abcdef123456"

    # Verify edge recorded
    edge = next((e for e in graph._edges if e["relationship"] == "HAS_REPOSITORY"), None)
    assert edge is not None
    assert edge["source"] == "project:autonomous-rover"
    assert edge["target"] == "git_repo:autonomous-rover"

    # Verify retrieval
    retrieved = await graph.get_git_repository("autonomous-rover")
    assert retrieved is not None
    assert retrieved.current_commit == "abcdef123456"


@pytest.mark.anyio
async def test_github_remote_graph_relationship():
    """Test saving GitHubRepository and linking GitRepository -> GitHubRepository."""
    graph = GitGraphRepository()

    gh_repo = GitHubRepository(
        repository_id="gh_acme_rover",
        owner="acme",
        name="rover",
        full_name="acme/rover",
        visibility=RepositoryVisibility.PUBLIC,
        default_branch="main",
        html_url="https://github.com/acme/rover",
        clone_url="https://github.com/acme/rover.git",
    )

    gh_model = await graph.save_github_repository("autonomous-rover", gh_repo)
    assert gh_model.full_name == "acme/rover"

    edge = next((e for e in graph._edges if e["relationship"] == "HAS_REMOTE"), None)
    assert edge is not None
    assert edge["source"] == "git_repo:autonomous-rover"
    assert edge["target"] == "github_repo:acme_rover"


@pytest.mark.anyio
async def test_git_commit_and_snapshot_graph():
    """Test saving current commit version reference and deterministic snapshot in graph."""
    graph = GitGraphRepository()

    commit_model = await graph.save_commit_reference(
        project_id="autonomous-rover",
        commit_hash="8f23a91b4c5de678",
        message="Add thermal PINN model",
        author="Lead Engineer",
        branch="main",
    )
    assert commit_model.commit_hash == "8f23a91b4c5de678"

    edge = next((e for e in graph._edges if e["relationship"] == "CURRENT_VERSION"), None)
    assert edge is not None
    assert edge["target"] == "git_commit:8f23a91b4c5d"

    snapshot = ProjectSnapshot(
        snapshot_id="snap_1234567890ab",
        project_id="autonomous-rover",
        project_version="0.3.0",
        git_commit="8f23a91b4c5de678",
        schema_version=1,
    )
    snap_model = await graph.save_project_snapshot(snapshot)
    assert snap_model.project_version == "0.3.0"
    assert snap_model.git_commit == "8f23a91b4c5de678"
