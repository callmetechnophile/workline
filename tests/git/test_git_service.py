"""Tests for controlled local Git service operations."""

from pathlib import Path
import pytest

from backend.workline.git.errors import GitError, RepositoryNotFoundError, UncommittedChangesError
from backend.workline.git.models import GitSyncStatus
from backend.workline.git.service import GitService


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Fixture providing an initialized local Git repository."""
    svc = GitService()
    svc.initialize_repository(tmp_path, initial_branch="main")
    return tmp_path


def test_git_repository_initialization(tmp_path: Path):
    """Test repository creation, default branch setup, and is_repository check."""
    svc = GitService()
    assert svc.is_repository(tmp_path) is False

    res = svc.initialize_repository(tmp_path, initial_branch="main")
    assert res.success is True
    assert svc.is_repository(tmp_path) is True
    assert svc.get_current_branch(tmp_path) == "main"


def test_git_status_clean_and_modified(temp_repo: Path):
    """Test status detection for clean working tree, untracked files, staged files, and modified files."""
    svc = GitService()

    # Initial empty status
    status = svc.get_status(temp_repo)
    assert status.branch == "main"
    assert status.is_clean is True

    # Create untracked file
    test_file = temp_repo / "README.md"
    test_file.write_text("# Test Project", encoding="utf-8")

    status2 = svc.get_status(temp_repo)
    assert status2.is_clean is False
    assert "README.md" in status2.untracked_files

    # Stage file
    svc.stage_files(temp_repo, ["README.md"])
    status3 = svc.get_status(temp_repo)
    assert "README.md" in status3.staged_files

    # Commit file
    commit = svc.create_commit(temp_repo, "Initial test commit", scan_secrets=True)
    assert commit.commit_hash is not None
    assert len(commit.short_hash) == 7
    assert commit.message == "Initial test commit"

    status4 = svc.get_status(temp_repo)
    assert status4.is_clean is True
    assert status4.current_commit == commit.commit_hash


def test_git_commit_and_log(temp_repo: Path):
    """Test multiple commits and log retrieval with limit."""
    svc = GitService()

    for i in range(3):
        f = temp_repo / f"file_{i}.txt"
        f.write_text(f"content {i}", encoding="utf-8")
        svc.stage_files(temp_repo)
        svc.create_commit(temp_repo, f"Commit number {i}", author_name="Dev User", author_email="dev@test.local")

    commits = svc.get_log(temp_repo, limit=2)
    assert len(commits) == 2
    assert commits[0].message == "Commit number 2"
    assert commits[1].message == "Commit number 1"
    assert commits[0].author == "Dev User"

    all_commits = svc.get_log(temp_repo, limit=10)
    assert len(all_commits) == 3


def test_git_branch_operations(temp_repo: Path):
    """Test branch creation, listing, switching, and deletion."""
    svc = GitService()

    # Create initial commit so HEAD exists
    (temp_repo / "init.txt").write_text("hello", encoding="utf-8")
    svc.stage_files(temp_repo)
    svc.create_commit(temp_repo, "Initial commit")

    # Create branch
    res_b = svc.create_branch(temp_repo, "feature/power-supply")
    assert res_b.success is True

    branches = svc.list_branches(temp_repo)
    branch_names = [b.name for b in branches]
    assert "main" in branch_names
    assert "feature/power-supply" in branch_names

    # Switch branch
    res_sw = svc.switch_branch(temp_repo, "feature/power-supply")
    assert res_sw.success is True
    assert svc.get_current_branch(temp_repo) == "feature/power-supply"

    # Switch back to main and delete feature branch
    svc.switch_branch(temp_repo, "main")
    res_del = svc.delete_branch(temp_repo, "feature/power-supply")
    assert res_del.success is True

    branches_after = svc.list_branches(temp_repo)
    assert "feature/power-supply" not in [b.name for b in branches_after]


def test_git_tag_operations(temp_repo: Path):
    """Test tag creation, listing, and commit reference linking."""
    svc = GitService()

    (temp_repo / "code.py").write_text("print('hello')", encoding="utf-8")
    svc.stage_files(temp_repo)
    c1 = svc.create_commit(temp_repo, "Code commit")

    tag = svc.create_tag(temp_repo, "v0.1.0", message="Release version 0.1.0")
    assert tag.name == "v0.1.0"
    assert tag.commit_hash == c1.commit_hash

    tags = svc.list_tags(temp_repo)
    assert len(tags) == 1
    assert tags[0].name == "v0.1.0"


def test_git_remote_configuration(temp_repo: Path):
    """Test setting, getting, and removing Git remotes."""
    svc = GitService()

    assert svc.get_remote(temp_repo, "origin") is None

    res = svc.set_remote(temp_repo, "origin", "https://github.com/acme/rover.git")
    assert res.success is True
    assert svc.get_remote(temp_repo, "origin") == "https://github.com/acme/rover.git"

    # Update remote
    res2 = svc.set_remote(temp_repo, "origin", "git@github.com:acme/rover.git")
    assert res2.success is True
    assert svc.get_remote(temp_repo, "origin") == "git@github.com:acme/rover.git"

    # Remove remote
    res3 = svc.remove_remote(temp_repo, "origin")
    assert res3.success is True
    assert svc.get_remote(temp_repo, "origin") is None


def test_git_local_push_and_pull(tmp_path: Path):
    """Test push and pull between two local repositories acting as remote and local."""
    svc = GitService()

    # Remote bare repository
    remote_path = tmp_path / "remote.git"
    remote_path.mkdir()
    svc._run(remote_path, ["init", "--bare", "-b", "main"])

    # Local repository 1
    local1 = tmp_path / "local1"
    svc.initialize_repository(local1, "main")
    (local1 / "doc.md").write_text("# Project Docs", encoding="utf-8")
    svc.stage_files(local1)
    svc.create_commit(local1, "First commit in local1")

    svc.set_remote(local1, "origin", str(remote_path))
    push_res = svc.push(local1, "origin", "main", set_upstream=True)
    assert push_res.success is True

    # Local repository 2 clones/pulls
    local2 = tmp_path / "local2"
    svc.initialize_repository(local2, "main")
    svc.set_remote(local2, "origin", str(remote_path))
    pull_res = svc.pull(local2, "origin", "main")
    assert pull_res.success is True
    assert (local2 / "doc.md").exists()
    assert (local2 / "doc.md").read_text(encoding="utf-8") == "# Project Docs"


def test_pull_blocked_on_uncommitted_changes(temp_repo: Path):
    """Test that pulling with uncommitted changes raises UncommittedChangesError."""
    svc = GitService()
    (temp_repo / "dirty.txt").write_text("uncommitted edits", encoding="utf-8")
    # File is untracked / dirty
    with pytest.raises(UncommittedChangesError):
        svc.pull(temp_repo, "origin", "main")
