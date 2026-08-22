"""Workline Native Git & GitHub Project Versioning Layer."""

from backend.workline.git.errors import (
    GitConflictError,
    GitError,
    GitHubAuthError,
    GitHubRepoExistsError,
    InvalidRepoNameError,
    RemoteNotFoundError,
    RepositoryNotFoundError,
    SecretDetectedError,
    UncommittedChangesError,
    UnsafeGitCommandError,
)
from backend.workline.git.github.auth import GitHubAuthStatus, check_github_auth
from backend.workline.git.github.client import GitHubClient, github_client
from backend.workline.git.github.repository import GitHubRepositoryService, github_repo_service
from backend.workline.git.models import (
    GitBranch,
    GitCommit,
    GitHubRepository,
    GitRepository,
    GitStatus,
    GitSyncStatus,
    GitTag,
    ProjectGitHubManifest,
    ProjectGitManifest,
    ProjectSnapshot,
    RepositoryVisibility,
    WorklineToonManifest,
)
from backend.workline.git.policies import SecretScanner, generate_default_gitignore, validate_repository_name
from backend.workline.git.repository import ProjectRepositoryManager, project_repo_manager
from backend.workline.git.service import GitResult, GitService, git_service
from backend.workline.git.toon import ToonSerializer

__all__ = [
    "GitService",
    "git_service",
    "GitResult",
    "ProjectRepositoryManager",
    "project_repo_manager",
    "GitHubClient",
    "github_client",
    "GitHubRepositoryService",
    "github_repo_service",
    "ToonSerializer",
    "SecretScanner",
    "validate_repository_name",
    "generate_default_gitignore",
    "check_github_auth",
    "GitHubAuthStatus",
    "GitError",
    "RepositoryNotFoundError",
    "SecretDetectedError",
    "UncommittedChangesError",
    "GitHubAuthError",
    "GitHubRepoExistsError",
    "InvalidRepoNameError",
    "RemoteNotFoundError",
    "GitConflictError",
    "UnsafeGitCommandError",
    "GitCommit",
    "GitBranch",
    "GitTag",
    "GitStatus",
    "GitSyncStatus",
    "GitRepository",
    "GitHubRepository",
    "ProjectSnapshot",
    "RepositoryVisibility",
    "WorklineToonManifest",
    "ProjectGitManifest",
    "ProjectGitHubManifest",
]
