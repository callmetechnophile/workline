"""GitHub Authentication state inspector using GitHub CLI or non-stored environment sessions."""

import os
import re
import shutil
import subprocess
from typing import Optional
from pydantic import BaseModel


class GitHubAuthStatus(BaseModel):
    """GitHub authentication status container."""
    authenticated: bool = False
    username: Optional[str] = None
    auth_method: str = "none"  # "cli", "env", "none"
    error_message: Optional[str] = None
    gh_installed: bool = False


def is_gh_cli_available() -> bool:
    """Check if the official GitHub CLI ('gh') is installed on PATH."""
    return shutil.which("gh") is not None


def check_github_auth() -> GitHubAuthStatus:
    """
    Detects if the user has an active authenticated GitHub session.
    1. Checks official GitHub CLI (`gh auth status`)
    2. Fallback to GITHUB_TOKEN / GH_TOKEN environment variable if present
    3. Never stores secrets or copies credentials to disk/database.
    """
    gh_available = is_gh_cli_available()

    # 1. Try GitHub CLI
    if gh_available:
        try:
            res = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                shell=False,
                timeout=10.0,
            )
            output = (res.stdout or "") + (res.stderr or "")

            # Look for logged in username: e.g. "Logged in to github.com account <username>"
            match = re.search(r"account\s+([A-Za-z0-9-_]+)", output, re.IGNORECASE)
            username = match.group(1) if match else None

            if not username:
                # Alternate pattern: "Logged in to github.com as <username>"
                match2 = re.search(r"as\s+([A-Za-z0-9-_]+)", output, re.IGNORECASE)
                username = match2.group(1) if match2 else None

            is_auth = (res.returncode == 0) or (username is not None)
            if is_auth:
                return GitHubAuthStatus(
                    authenticated=True,
                    username=username or "github-user",
                    auth_method="cli",
                    gh_installed=True,
                )
            else:
                return GitHubAuthStatus(
                    authenticated=False,
                    auth_method="cli",
                    error_message=output.strip() or "GitHub CLI is not logged in. Run 'gh auth login'.",
                    gh_installed=True,
                )
        except Exception as exc:
            pass

    # 2. Fallback: Environment variable session (e.g. CI/CD or temporary shell session)
    env_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if env_token:
        return GitHubAuthStatus(
            authenticated=True,
            username=os.environ.get("GITHUB_USER") or "github-actions-user",
            auth_method="env",
            gh_installed=gh_available,
        )

    # 3. Not authenticated
    action_msg = "Run 'gh auth login' or install the GitHub CLI from https://cli.github.com" if not gh_available else "Run 'gh auth login' to authenticate with GitHub."
    return GitHubAuthStatus(
        authenticated=False,
        auth_method="none",
        error_message=action_msg,
        gh_installed=gh_available,
    )
