"""GitHub repository management service for connecting, initializing, and syncing projects."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from backend.workline.git.errors import (
    GitHubAuthError,
    GitHubRepoExistsError,
    GitError,
    RepositoryNotFoundError,
)
from backend.workline.git.github.client import GitHubClient, github_client
from backend.workline.git.github.remote import normalize_github_url, parse_github_repo_spec
from backend.workline.git.models import GitHubRepository, RepositoryVisibility
from backend.workline.git.repository import ProjectRepositoryManager, project_repo_manager
from backend.workline.git.service import GitResult, GitService, git_service


class GitHubRepositoryService:
    """Orchestrates GitHub repository creation, connecting existing remotes, and manifest synchronization."""

    def __init__(
        self,
        git: GitService = git_service,
        gh: GitHubClient = github_client,
        repo_mgr: ProjectRepositoryManager = project_repo_manager,
    ):
        self.git = git
        self.gh = gh
        self.repo_mgr = repo_mgr

    def initialize_github_repository(
        self,
        project_path: Path,
        repo_name: Optional[str] = None,
        private: bool = True,
        description: str = "",
        auto_push: bool = True,
    ) -> Tuple[GitHubRepository, Optional[GitResult]]:
        """
        Creates a new GitHub repository, sets local remote 'origin', and pushes initial commit.
        """
        p = Path(project_path).resolve()
        if not self.git.is_repository(p):
            raise RepositoryNotFoundError(f"Project directory '{p}' is not a Git repository. Run 'wline init' first.")

        # 1. Inspect manifest / determine repo name
        manifest = self.repo_mgr.load_toon_manifest(p)
        target_name = repo_name or (manifest.project_id if manifest else p.name)

        # 2. Check GitHub Authentication
        auth = self.gh.authenticate()
        if not auth.authenticated:
            raise GitHubAuthError(f"GitHub authentication required: {auth.error_message}")

        # 3. Create remote GitHub repository
        gh_repo = self.gh.create_repository(
            name=target_name,
            private=private,
            description=description,
        )

        # 4. Configure local remote 'origin'
        self.git.set_remote(p, name="origin", url=gh_repo.clone_url)

        # 5. Push initial commit to origin
        push_res = None
        if auto_push:
            curr_branch = self.git.get_current_branch(p) or "main"
            push_res = self.git.push(p, remote="origin", branch=curr_branch, set_upstream=True)

        # 6. Update .workline/project.toon
        if manifest:
            manifest.github.connected = True
            manifest.github.owner = gh_repo.owner
            manifest.github.repository = gh_repo.name
            manifest.github.remote = gh_repo.clone_url
            self.repo_mgr.save_toon_manifest(p, manifest)

        return gh_repo, push_res

    def connect_existing_repository(
        self,
        project_path: Path,
        repo_spec: str,
    ) -> GitHubRepository:
        """
        Connects an existing GitHub repository to the local project.
        """
        p = Path(project_path).resolve()
        if not self.git.is_repository(p):
            raise RepositoryNotFoundError(f"Directory '{p}' is not a Git repository.")

        owner, repo_name = parse_github_repo_spec(repo_spec)
        auth = self.gh.authenticate()
        target_owner = owner or (auth.username if auth.authenticated else "user")

        clone_url = normalize_github_url(target_owner, repo_name)
        html_url = f"https://github.com/{target_owner}/{repo_name}"

        # Configure origin
        self.git.set_remote(p, name="origin", url=clone_url)

        gh_repo = GitHubRepository(
            repository_id=f"gh_{target_owner}_{repo_name}",
            owner=target_owner,
            name=repo_name,
            full_name=f"{target_owner}/{repo_name}",
            visibility=RepositoryVisibility.PRIVATE,
            default_branch="main",
            html_url=html_url,
            clone_url=clone_url,
            ssh_url=normalize_github_url(target_owner, repo_name, use_ssh=True),
        )

        # Update manifest
        manifest = self.repo_mgr.load_toon_manifest(p)
        if manifest:
            manifest.github.connected = True
            manifest.github.owner = target_owner
            manifest.github.repository = repo_name
            manifest.github.remote = clone_url
            self.repo_mgr.save_toon_manifest(p, manifest)

        return gh_repo

    def disconnect_repository(self, project_path: Path) -> None:
        """Disconnects remote origin and updates manifest."""
        p = Path(project_path).resolve()
        self.git.remove_remote(p, "origin")

        manifest = self.repo_mgr.load_toon_manifest(p)
        if manifest:
            manifest.github.connected = False
            manifest.github.owner = None
            manifest.github.repository = None
            manifest.github.remote = None
            self.repo_mgr.save_toon_manifest(p, manifest)


# Module-level singleton
github_repo_service = GitHubRepositoryService()
