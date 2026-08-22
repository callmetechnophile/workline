"""GitHub Remote Integration Subsystem for Workline."""

from backend.workline.git.github.auth import GitHubAuthStatus, check_github_auth
from backend.workline.git.github.client import GitHubClient, github_client
from backend.workline.git.github.remote import normalize_github_url, parse_github_repo_spec
from backend.workline.git.github.repository import GitHubRepositoryService

__all__ = [
    "GitHubAuthStatus",
    "check_github_auth",
    "GitHubClient",
    "github_client",
    "normalize_github_url",
    "parse_github_repo_spec",
    "GitHubRepositoryService",
]
