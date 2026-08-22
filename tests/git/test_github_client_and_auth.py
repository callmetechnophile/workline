"""Tests for GitHub client, authentication detection, repository creation, and remote configuration."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from backend.workline.git.errors import (
    GitHubAuthError,
    GitHubRepoExistsError,
    InvalidRepoNameError,
)
from backend.workline.git.github.auth import GitHubAuthStatus, check_github_auth
from backend.workline.git.github.client import GitHubClient
from backend.workline.git.github.remote import (
    get_html_url,
    normalize_github_url,
    parse_github_repo_spec,
)
from backend.workline.git.github.repository import GitHubRepositoryService
from backend.workline.git.models import RepositoryVisibility
from backend.workline.git.policies import validate_repository_name
from backend.workline.git.repository import ProjectRepositoryManager


def test_github_repo_spec_parsing_and_normalization():
    """Test parsing varied repository spec formats into canonical URLs."""
    # Simple name
    owner1, name1 = parse_github_repo_spec("autonomous-rover")
    assert owner1 is None
    assert name1 == "autonomous-rover"

    # owner/repo
    owner2, name2 = parse_github_repo_spec("acme/autonomous-rover")
    assert owner2 == "acme"
    assert name2 == "autonomous-rover"

    # HTTPS URL with .git
    owner3, name3 = parse_github_repo_spec("https://github.com/acme/autonomous-rover.git")
    assert owner3 == "acme"
    assert name3 == "autonomous-rover"

    # SSH URL
    owner4, name4 = parse_github_repo_spec("git@github.com:acme/autonomous-rover.git")
    assert owner4 == "acme"
    assert name4 == "autonomous-rover"

    # Normalization
    https_url = normalize_github_url("acme", "autonomous-rover")
    assert https_url == "https://github.com/acme/autonomous-rover.git"

    ssh_url = normalize_github_url("acme", "autonomous-rover", use_ssh=True)
    assert ssh_url == "git@github.com:acme/autonomous-rover.git"

    html_url = get_html_url("acme", "autonomous-rover")
    assert html_url == "https://github.com/acme/autonomous-rover"


def test_repository_name_validation():
    """Test validation of GitHub repository naming rules."""
    assert validate_repository_name("autonomous-rover") == "autonomous-rover"
    assert validate_repository_name("rover_v2.0") == "rover_v2.0"

    with pytest.raises(InvalidRepoNameError):
        validate_repository_name("")

    with pytest.raises(InvalidRepoNameError):
        validate_repository_name("-invalid-start")

    with pytest.raises(InvalidRepoNameError):
        validate_repository_name("invalid-end-")

    with pytest.raises(InvalidRepoNameError):
        validate_repository_name("invalid name with spaces")


def test_github_auth_detection():
    """Test detecting authentication status from environment or missing auth."""
    # When no token and gh not available / logged out
    with patch("backend.workline.git.github.auth.is_gh_cli_available", return_value=False):
        with patch.dict("os.environ", {}, clear=True):
            status = check_github_auth()
            assert status.authenticated is False

    # When GITHUB_TOKEN environment variable is set
    with patch.dict("os.environ", {"GITHUB_TOKEN": "mock-gh-token-12345", "GITHUB_USER": "test-dev"}):
        status_env = check_github_auth()
        assert status_env.authenticated is True
        assert status_env.username == "test-dev"
        assert status_env.auth_method == "env"


def test_github_client_create_repository_unauthenticated():
    """Test that creating a repository without authentication raises GitHubAuthError."""
    client = GitHubClient()
    with patch.object(client, "authenticate", return_value=GitHubAuthStatus(authenticated=False, error_message="Not logged in")):
        with pytest.raises(GitHubAuthError):
            client.create_repository(name="test-repo")


def test_github_client_create_repository_already_exists():
    """Test that creating an already existing repository raises GitHubRepoExistsError without overwriting."""
    client = GitHubClient()
    auth = GitHubAuthStatus(authenticated=True, username="test-user", auth_method="env")

    with patch.object(client, "authenticate", return_value=auth):
        with patch.object(client, "repository_exists", return_value=True):
            with pytest.raises(GitHubRepoExistsError) as exc_info:
                client.create_repository(name="existing-rover")
            assert exc_info.value.repo_name == "existing-rover"


def test_github_repository_init_and_connect_flow(tmp_path: Path):
    """Test GitHub project initialization and existing repo connection flow."""
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(tmp_path, "robot-arm", "Robot Arm")

    gh_client = GitHubClient()
    auth = GitHubAuthStatus(authenticated=True, username="robot-team", auth_method="env")

    with patch.object(gh_client, "authenticate", return_value=auth):
        with patch.object(gh_client, "repository_exists", return_value=False):
            with patch("backend.workline.git.github.client.is_gh_cli_available", return_value=False):
                gh_service = GitHubRepositoryService(gh=gh_client, repo_mgr=mgr)

                # Initialize GitHub repository (without auto-push to non-existent remote)
                repo, _ = gh_service.initialize_github_repository(
                    project_path=tmp_path,
                    repo_name="robot-arm",
                    private=True,
                    description="Robotic arm controller",
                    auto_push=False,
                )

                assert repo.owner == "robot-team"
                assert repo.name == "robot-arm"
                assert repo.full_name == "robot-team/robot-arm"
                assert repo.visibility == RepositoryVisibility.PRIVATE

                # Verify manifest updated
                manifest = mgr.load_toon_manifest(tmp_path)
                assert manifest.github.connected is True
                assert manifest.github.owner == "robot-team"
                assert manifest.github.repository == "robot-arm"

                # Disconnect repository
                gh_service.disconnect_repository(tmp_path)
                manifest_disc = mgr.load_toon_manifest(tmp_path)
                assert manifest_disc.github.connected is False

                # Connect existing repository
                gh_service.connect_existing_repository(tmp_path, "enterprise/robot-arm-fork")
                manifest_conn = mgr.load_toon_manifest(tmp_path)
                assert manifest_conn.github.connected is True
                assert manifest_conn.github.owner == "enterprise"
                assert manifest_conn.github.repository == "robot-arm-fork"
