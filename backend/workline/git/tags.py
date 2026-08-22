"""Git tag and release marking operations."""

from pathlib import Path
from typing import List, Optional
from backend.workline.git.models import GitTag
from backend.workline.git.service import GitService, git_service


def create_release_tag(
    project_path: Path,
    tag_name: str,
    message: Optional[str] = None,
    service: GitService = git_service,
) -> GitTag:
    """Create a tag corresponding to a release or milestone commit."""
    return service.create_tag(project_path, tag_name, message=message)


def list_release_tags(project_path: Path, service: GitService = git_service) -> List[GitTag]:
    """List all tags in the repository."""
    return service.list_tags(project_path)
