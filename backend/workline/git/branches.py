"""Git branch management operations."""

from pathlib import Path
from typing import List
from backend.workline.git.models import GitBranch
from backend.workline.git.service import GitResult, GitService, git_service


def list_branches(project_path: Path, service: GitService = git_service) -> List[GitBranch]:
    """List all local branches."""
    return service.list_branches(project_path)


def create_branch(project_path: Path, branch_name: str, service: GitService = git_service) -> GitResult:
    """Create a new branch."""
    return service.create_branch(project_path, branch_name)


def checkout_branch(
    project_path: Path,
    branch_name: str,
    create: bool = False,
    service: GitService = git_service,
) -> GitResult:
    """Switch or checkout branch."""
    return service.switch_branch(project_path, branch_name, create=create)


def delete_branch(
    project_path: Path,
    branch_name: str,
    force: bool = False,
    service: GitService = git_service,
) -> GitResult:
    """Delete a branch."""
    return service.delete_branch(project_path, branch_name, force=force)
