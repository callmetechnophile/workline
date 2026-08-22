"""Git status and working tree inspection operations."""

from pathlib import Path
from backend.workline.git.models import GitStatus
from backend.workline.git.service import GitService, git_service


def get_repository_status(project_path: Path, service: GitService = git_service) -> GitStatus:
    """Retrieve detailed working tree and remote synchronization status."""
    return service.get_status(project_path)
