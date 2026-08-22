"""Git remote configuration, push, and pull operations."""

from pathlib import Path
from typing import Optional
from backend.workline.git.service import GitResult, GitService, git_service


def configure_remote(
    project_path: Path,
    name: str = "origin",
    url: str = "",
    service: GitService = git_service,
) -> GitResult:
    """Add or update a Git remote."""
    return service.set_remote(project_path, name=name, url=url)


def get_remote_url(
    project_path: Path,
    name: str = "origin",
    service: GitService = git_service,
) -> Optional[str]:
    """Retrieve remote URL."""
    return service.get_remote(project_path, name=name)


def push_to_remote(
    project_path: Path,
    remote: str = "origin",
    branch: Optional[str] = None,
    set_upstream: bool = False,
    tags: bool = False,
    service: GitService = git_service,
) -> GitResult:
    """Push commits and tags to remote."""
    return service.push(
        path=project_path,
        remote=remote,
        branch=branch,
        set_upstream=set_upstream,
        tags=tags,
    )


def pull_from_remote(
    project_path: Path,
    remote: str = "origin",
    branch: Optional[str] = None,
    service: GitService = git_service,
) -> GitResult:
    """Pull changes from remote."""
    return service.pull(project_path, remote=remote, branch=branch)
