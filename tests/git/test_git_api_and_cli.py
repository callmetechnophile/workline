"""Tests for Git REST API endpoints and CLI subcommands."""

from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from backend.main import app
from backend.workline.git.github.auth import GitHubAuthStatus
from backend.workline.git.models import GitHubRepository, RepositoryVisibility
from backend.workline.git.repository import project_repo_manager
from cli.wline.core.manifest import ProjectManifest, save_manifest
from cli.wline.core.paths import get_workspace_dir, set_active_project_name
from cli.wline.core.workspace import create_project
from cli.wline.main import app as cli_app


def test_git_cli_full_workflow(tmp_path: Path):
    """Test end-to-end CLI workflow: init -> status -> commit -> log -> branch -> tag -> version -> snapshot -> release."""
    runner = CliRunner()

    with patch.dict("os.environ", {"WORKLINE_WORKSPACE": str(tmp_path)}):
        # 1. wline init <project>
        res_init = runner.invoke(cli_app, ["init", "drone-controller"])
        assert res_init.exit_code == 0
        assert "WORKLINE PROJECT INITIALIZATION" in res_init.stdout
        assert "Git repository" in res_init.stdout
        assert "Project ready." in res_init.stdout

        # 2. wline git status
        res_status = runner.invoke(cli_app, ["git", "status", "--project", "drone-controller"])
        assert res_status.exit_code == 0
        assert "WORKLINE GIT STATUS" in res_status.stdout
        assert "CLEAN" in res_status.stdout

        # 3. Create file and wline git commit
        proj_dir = tmp_path / "drone-controller"
        (proj_dir / "firmware" / "main.c").write_text("void main() {}", encoding="utf-8")

        res_commit = runner.invoke(cli_app, ["git", "commit", "-m", "Add flight controller main loop", "--project", "drone-controller"])
        assert res_commit.exit_code == 0
        assert "Commit created" in res_commit.stdout

        # 4. wline git log
        res_log = runner.invoke(cli_app, ["git", "log", "--project", "drone-controller"])
        assert res_log.exit_code == 0
        assert "flight controller" in res_log.stdout

        # 5. wline git branch create & checkout
        res_branch = runner.invoke(cli_app, ["git", "branch", "create", "feature/pid-tuning", "--project", "drone-controller"])
        assert res_branch.exit_code == 0
        assert "created" in res_branch.stdout

        res_checkout = runner.invoke(cli_app, ["git", "checkout", "feature/pid-tuning", "--project", "drone-controller"])
        assert res_checkout.exit_code == 0
        assert "Switched to branch" in res_checkout.stdout

        # 6. wline git tag
        res_tag = runner.invoke(cli_app, ["git", "tag", "v0.1.0", "-m", "Milestone 1", "--project", "drone-controller"])
        assert res_tag.exit_code == 0
        assert "Git tag created" in res_tag.stdout

        # 7. wline version
        res_ver = runner.invoke(cli_app, ["version", "--project", "drone-controller"])
        assert res_ver.exit_code == 0
        assert "WORKLINE VERSION" in res_ver.stdout
        assert "Project:" in res_ver.stdout
        assert "Git:" in res_ver.stdout

        # 8. wline snapshot
        res_snap = runner.invoke(cli_app, ["snapshot", "--project", "drone-controller"])
        assert res_snap.exit_code == 0
        assert "PROJECT SNAPSHOT CREATED" in res_snap.stdout

        # 9. wline release
        res_rel = runner.invoke(cli_app, ["release", "0.2.0", "--project", "drone-controller", "-m", "Version 0.2.0 release"])
        assert res_rel.exit_code == 0
        assert "RELEASE v0.2.0 CREATED" in res_rel.stdout


def test_github_cli_workflow(tmp_path: Path):
    """Test GitHub CLI subcommands: auth status, init, connect, remote."""
    runner = CliRunner()

    with patch.dict("os.environ", {"WORKLINE_WORKSPACE": str(tmp_path)}):
        runner.invoke(cli_app, ["init", "rover-core"])
        proj_dir = tmp_path / "rover-core"

        # 1. wline github auth status
        with patch("cli.wline.commands.github.check_github_auth", return_value=GitHubAuthStatus(authenticated=True, username="rover-dev", auth_method="cli")):
            res_auth = runner.invoke(cli_app, ["github", "auth", "status"])
            assert res_auth.exit_code == 0
            assert "Authenticated" in res_auth.stdout
            assert "rover-dev" in res_auth.stdout

        # 2. wline github init
        mock_repo = GitHubRepository(
            repository_id="gh_rover-dev_rover-core",
            owner="rover-dev",
            name="rover-core",
            full_name="rover-dev/rover-core",
            visibility=RepositoryVisibility.PRIVATE,
            html_url="https://github.com/rover-dev/rover-core",
            clone_url="https://github.com/rover-dev/rover-core.git",
        )
        with patch("cli.wline.commands.github.github_repo_service.initialize_github_repository", return_value=(mock_repo, None)):
            res_gh_init = runner.invoke(cli_app, ["github", "init", "--project", "rover-core", "--no-push"])
            assert res_gh_init.exit_code == 0
            assert "Repository created" in res_gh_init.stdout
            assert "rover-dev/rover-core" in res_gh_init.stdout

        # 3. wline github remote
        res_remote = runner.invoke(cli_app, ["github", "remote", "--project", "rover-core"])
        assert res_remote.exit_code == 0

        # 4. wline github connect
        with patch("cli.wline.commands.github.github_repo_service.connect_existing_repository", return_value=mock_repo):
            res_conn = runner.invoke(cli_app, ["github", "connect", "rover-dev/rover-core", "--project", "rover-core"])
            assert res_conn.exit_code == 0
            assert "Connected to existing GitHub repository" in res_conn.stdout


def test_git_fastapi_endpoints(tmp_path: Path):
    """Test REST API routes for Git status, commits, branches, tags, snapshots, and releases."""
    client = TestClient(app)

    with patch.dict("os.environ", {"WORKLINE_WORKSPACE": str(tmp_path)}):
        # Create test project
        proj_dir = tmp_path / "api-rover"
        project_repo_manager.init_project_git(proj_dir, "api-rover", "API Rover")

        # 1. GET /api/git/auth/status
        with patch("backend.workline.api.git.check_github_auth", return_value=GitHubAuthStatus(authenticated=True, username="api-dev", auth_method="env")):
            res_auth = client.get("/api/git/auth/status")
            assert res_auth.status_code == 200
            assert res_auth.json()["authenticated"] is True

        # 2. GET /api/git/{project_id}/status
        res_status = client.get("/api/git/api-rover/status")
        assert res_status.status_code == 200
        assert res_status.json()["is_clean"] is True
        assert res_status.json()["branch"] == "main"

        # 3. POST /api/git/{project_id}/commit
        (proj_dir / "new_file.txt").write_text("data", encoding="utf-8")
        res_commit = client.post("/api/git/api-rover/commit", json={"message": "Add test data"})
        assert res_commit.status_code == 200
        assert res_commit.json()["message"] == "Add test data"

        # 4. GET /api/git/{project_id}/log
        res_log = client.get("/api/git/api-rover/log?limit=5")
        assert res_log.status_code == 200
        assert len(res_log.json()) >= 2

        # 5. POST /api/git/{project_id}/branches
        res_branch = client.post("/api/git/api-rover/branches", json={"name": "develop"})
        assert res_branch.status_code == 200

        # 6. GET /api/git/{project_id}/branches
        res_branches = client.get("/api/git/api-rover/branches")
        assert res_branches.status_code == 200
        assert any(b["name"] == "develop" for b in res_branches.json())

        # 7. POST /api/git/{project_id}/tags
        res_tag = client.post("/api/git/api-rover/tags", json={"name": "v0.1.0", "message": "Initial release"})
        assert res_tag.status_code == 200

        # 8. GET /api/git/{project_id}/tags
        res_tags = client.get("/api/git/api-rover/tags")
        assert res_tags.status_code == 200
        assert any(t["name"] == "v0.1.0" for t in res_tags.json())

        # 9. POST /api/git/{project_id}/snapshot
        res_snap = client.post("/api/git/api-rover/snapshot")
        assert res_snap.status_code == 200
        assert "snapshot_id" in res_snap.json()

        # 10. POST /api/git/{project_id}/release
        res_rel = client.post("/api/git/api-rover/release", json={"version": "0.3.0", "message": "Version 0.3.0 release"})
        assert res_rel.status_code == 200
        assert res_rel.json()["release_version"] == "0.3.0"
