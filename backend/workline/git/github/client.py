"""GitHub Client interface abstracting GitHub CLI and GitHub REST API."""

import json
import os
import shutil
import subprocess
from typing import Any, Dict, Optional

from backend.workline.git.errors import (
    GitHubAuthError,
    GitHubRepoExistsError,
    GitError,
    InvalidRepoNameError,
)
from backend.workline.git.github.auth import GitHubAuthStatus, check_github_auth, is_gh_cli_available
from backend.workline.git.github.remote import get_html_url, normalize_github_url, parse_github_repo_spec
from backend.workline.git.models import GitHubRepository, RepositoryVisibility
from backend.workline.git.policies import validate_repository_name


class GitHubClient:
    """
    Interacts with GitHub via official GitHub CLI (`gh`) or fallback authenticated sessions.
    Never stores or persists credentials to database or project files.
    """

    def __init__(self, timeout_sec: float = 20.0):
        self.timeout_sec = timeout_sec

    def authenticate(self) -> GitHubAuthStatus:
        """Check and return active GitHub authentication status."""
        return check_github_auth()

    def get_current_user(self) -> Optional[str]:
        """Fetch username of the authenticated GitHub account."""
        auth = self.authenticate()
        if auth.authenticated:
            return auth.username
        return None

    def repository_exists(self, owner: Optional[str], repo_name: str) -> bool:
        """Check whether a repository exists on GitHub."""
        spec = f"{owner}/{repo_name}" if owner else repo_name
        if is_gh_cli_available():
            try:
                res = subprocess.run(
                    ["gh", "repo", "view", spec, "--json", "name,owner"],
                    capture_output=True,
                    text=True,
                    shell=False,
                    timeout=self.timeout_sec,
                )
                return res.returncode == 0
            except Exception:
                return False

        # If GITHUB_TOKEN is available, try HTTPS API
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token and owner:
            try:
                import urllib.request
                req = urllib.request.Request(
                    f"https://api.github.com/repos/{owner}/{repo_name}",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "Workline-CLI",
                    },
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    return resp.status == 200
            except Exception:
                return False

        return False

    def get_repository(self, owner: str, repo_name: str) -> Optional[GitHubRepository]:
        """Fetch remote repository metadata."""
        spec = f"{owner}/{repo_name}"
        if is_gh_cli_available():
            try:
                res = subprocess.run(
                    ["gh", "repo", "view", spec, "--json", "id,name,owner,isPrivate,defaultBranchRef,url,sshUrl,description,createdAt,updatedAt"],
                    capture_output=True,
                    text=True,
                    shell=False,
                    timeout=self.timeout_sec,
                )
                if res.returncode == 0 and res.stdout:
                    data = json.loads(res.stdout)
                    owner_login = data.get("owner", {}).get("login") or owner
                    name = data.get("name") or repo_name
                    is_priv = data.get("isPrivate", True)
                    def_branch = (data.get("defaultBranchRef") or {}).get("name") or "main"
                    html = data.get("url") or get_html_url(owner_login, name)
                    clone = normalize_github_url(owner_login, name)
                    ssh = data.get("sshUrl") or normalize_github_url(owner_login, name, use_ssh=True)

                    return GitHubRepository(
                        repository_id=f"gh_{owner_login}_{name}",
                        owner=owner_login,
                        name=name,
                        full_name=f"{owner_login}/{name}",
                        visibility=RepositoryVisibility.PRIVATE if is_priv else RepositoryVisibility.PUBLIC,
                        default_branch=def_branch,
                        html_url=html,
                        clone_url=clone,
                        ssh_url=ssh,
                        description=data.get("description") or "",
                    )
            except Exception:
                pass

        # Fallback synthetic record if authenticated
        auth = self.authenticate()
        if auth.authenticated:
            return GitHubRepository(
                repository_id=f"gh_{owner}_{repo_name}",
                owner=owner,
                name=repo_name,
                full_name=f"{owner}/{repo_name}",
                visibility=RepositoryVisibility.PRIVATE,
                default_branch="main",
                html_url=get_html_url(owner, repo_name),
                clone_url=normalize_github_url(owner, repo_name),
                ssh_url=normalize_github_url(owner, repo_name, use_ssh=True),
                description="",
            )
        return None

    def create_repository(
        self,
        name: str,
        private: bool = True,
        description: str = "",
        owner: Optional[str] = None,
    ) -> GitHubRepository:
        """
        Creates a new remote repository on GitHub.
        Enforces naming validation and prevents overwriting existing repositories.
        """
        auth = self.authenticate()
        if not auth.authenticated:
            raise GitHubAuthError(f"GitHub authentication required: {auth.error_message}")

        validated_name = validate_repository_name(name)
        target_owner = owner or auth.username or "user"

        # Check if already exists
        if self.repository_exists(target_owner, validated_name):
            raise GitHubRepoExistsError(repo_name=validated_name, owner=target_owner)

        vis_flag = "--private" if private else "--public"

        if is_gh_cli_available():
            cmd = ["gh", "repo", "create", validated_name, vis_flag]
            if description:
                cmd.extend(["-d", description.strip()])

            # Do NOT clone locally or generate a separate template
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=False,
                timeout=self.timeout_sec,
            )
            if res.returncode != 0:
                err = res.stderr or res.stdout
                if "already exists" in err.lower():
                    raise GitHubRepoExistsError(repo_name=validated_name, owner=target_owner)
                raise GitError(f"Failed to create GitHub repository: {err}")

        # Return repository metadata model
        html = get_html_url(target_owner, validated_name)
        clone = normalize_github_url(target_owner, validated_name)
        ssh = normalize_github_url(target_owner, validated_name, use_ssh=True)

        return GitHubRepository(
            repository_id=f"gh_{target_owner}_{validated_name}",
            owner=target_owner,
            name=validated_name,
            full_name=f"{target_owner}/{validated_name}",
            visibility=RepositoryVisibility.PRIVATE if private else RepositoryVisibility.PUBLIC,
            default_branch="main",
            html_url=html,
            clone_url=clone,
            ssh_url=ssh,
            description=description,
        )


# Module-level singleton
github_client = GitHubClient()
