"""Git commit and history operations with secret scanning integration."""

from pathlib import Path
from typing import List, Optional
from backend.workline.git.models import GitCommit
from backend.workline.git.service import GitService, git_service


def make_commit(
    project_path: Path,
    message: str,
    author: str = "Workline Engineer",
    email: str = "engineer@workline.dev",
    stage_all: bool = True,
    scan_secrets: bool = True,
    service: GitService = git_service,
) -> GitCommit:
    """Create a validated commit with secret scanning policy check."""
    return service.create_commit(
        path=project_path,
        message=message,
        author_name=author,
        author_email=email,
        stage_all=stage_all,
        scan_secrets=scan_secrets,
    )


def list_commit_log(
    project_path: Path,
    limit: int = 10,
    service: GitService = git_service,
) -> List[GitCommit]:
    """Retrieve recent commit history log."""
    return service.get_log(project_path, limit=limit)
