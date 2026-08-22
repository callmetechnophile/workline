"""Pydantic data models for Git repository, commits, branches, tags, GitHub metadata, and TOON manifests."""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RepositoryVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"


class GitSyncStatus(str, Enum):
    UP_TO_DATE = "UP_TO_DATE"
    AHEAD = "AHEAD"
    BEHIND = "BEHIND"
    DIVERGED = "DIVERGED"
    UNTRACKED_REMOTE = "UNTRACKED_REMOTE"
    NO_REMOTE = "NO_REMOTE"


class GitCommit(BaseModel):
    """Git commit representation."""
    commit_hash: str
    short_hash: str
    message: str
    author: str = "Workline Engineer"
    email: str = "engineer@workline.dev"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    branch: Optional[str] = None


class GitBranch(BaseModel):
    """Git branch representation."""
    name: str
    is_current: bool = False
    commit_hash: Optional[str] = None


class GitTag(BaseModel):
    """Git tag / version release marker."""
    name: str
    commit_hash: str
    message: Optional[str] = ""
    tagger: Optional[str] = "Workline"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GitStatus(BaseModel):
    """Local repository working tree status."""
    is_clean: bool = True
    branch: str = "main"
    current_commit: Optional[str] = None
    short_commit: Optional[str] = None
    staged_files: List[str] = Field(default_factory=list)
    modified_files: List[str] = Field(default_factory=list)
    untracked_files: List[str] = Field(default_factory=list)
    remote_url: Optional[str] = None
    ahead: int = 0
    behind: int = 0
    sync_status: GitSyncStatus = GitSyncStatus.NO_REMOTE


class GitHubRepository(BaseModel):
    """Remote GitHub repository metadata."""
    repository_id: str
    owner: str
    name: str
    full_name: str
    visibility: RepositoryVisibility = RepositoryVisibility.PRIVATE
    default_branch: str = "main"
    html_url: str
    clone_url: str
    ssh_url: Optional[str] = None
    description: Optional[str] = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GitRepository(BaseModel):
    """Local Git repository descriptor and metadata."""
    repository_id: str
    project_id: str
    local_path: str
    default_branch: str = "main"
    current_branch: str = "main"
    current_commit: Optional[str] = None
    remote_url: Optional[str] = None
    last_sync: Optional[str] = None
    visibility: RepositoryVisibility = RepositoryVisibility.PRIVATE
    github_connected: bool = False
    github_repo: Optional[GitHubRepository] = None


class ProjectGitManifest(BaseModel):
    """Git section of .workline/project.toon."""
    initialized: bool = True
    current_branch: str = "main"
    current_commit: Optional[str] = None


class ProjectGitHubManifest(BaseModel):
    """GitHub section of .workline/project.toon."""
    connected: bool = False
    owner: Optional[str] = None
    repository: Optional[str] = None
    remote: Optional[str] = None


class WorklineToonManifest(BaseModel):
    """Full .workline/project.toon project manifest."""
    project_id: str
    project_name: str
    workline_version: str = "0.1.0"
    schema_version: int = 1
    project_version: str = "0.1.0"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    git: ProjectGitManifest = Field(default_factory=ProjectGitManifest)
    github: ProjectGitHubManifest = Field(default_factory=ProjectGitHubManifest)


class ProjectSnapshot(BaseModel):
    """Deterministic snapshot record capturing project state linked to git commit."""
    snapshot_id: str
    project_id: str
    project_version: str
    git_commit: str
    schema_version: int = 1
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data_summary: Dict[str, Any] = Field(default_factory=dict)
