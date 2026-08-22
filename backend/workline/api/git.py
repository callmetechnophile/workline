"""FastAPI REST API router for Git version control and GitHub integration."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.workline.git.github.auth import GitHubAuthStatus, check_github_auth
from backend.workline.git.github.repository import github_repo_service
from backend.workline.git.graph import git_graph_repo
from backend.workline.git.models import (
    GitBranch,
    GitCommit,
    GitHubRepository,
    GitRepository,
    GitStatus,
    GitTag,
    ProjectSnapshot,
    WorklineToonManifest,
)
from backend.workline.git.repository import project_repo_manager
from backend.workline.git.service import git_service
from cli.wline.core.paths import get_workspace_dir
from cli.wline.core.workspace import find_project

router = APIRouter(prefix="/api/git", tags=["Workline Git & GitHub Versioning"])


def _get_project_path(project_id: str) -> Path:
    found = find_project(project_id)
    if found:
        return found[0]
    ws_p = get_workspace_dir() / project_id
    if ws_p.exists():
        return ws_p
    raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")


class CommitRequest(BaseModel):
    message: str
    author: str = "Workline Engineer"
    email: str = "engineer@workline.dev"


class BranchRequest(BaseModel):
    name: str


class TagRequest(BaseModel):
    name: str
    message: Optional[str] = None


class GitHubInitRequest(BaseModel):
    name: Optional[str] = None
    private: bool = True
    description: Optional[str] = ""
    auto_push: bool = True


class GitHubConnectRequest(BaseModel):
    repo_spec: str


class ReleaseRequest(BaseModel):
    version: str
    message: Optional[str] = None


@router.get("/auth/status", response_model=GitHubAuthStatus)
async def get_github_auth_api():
    """Check active GitHub CLI and environment session authentication state."""
    return check_github_auth()


@router.get("/{project_id}/status", response_model=GitStatus)
async def get_git_status_api(project_id: str):
    """Fetch working tree, branch, commit, and remote synchronization status."""
    p_path = _get_project_path(project_id)
    try:
        return git_service.get_status(p_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{project_id}/log", response_model=List[GitCommit])
async def get_git_log_api(project_id: str, limit: int = 10):
    """Fetch project commit history log."""
    p_path = _get_project_path(project_id)
    return git_service.get_log(p_path, limit=limit)


@router.post("/{project_id}/commit", response_model=GitCommit)
async def create_git_commit_api(project_id: str, payload: CommitRequest):
    """Create a validated commit with secret scanning."""
    p_path = _get_project_path(project_id)
    try:
        commit = git_service.create_commit(
            path=p_path,
            message=payload.message,
            author_name=payload.author,
            author_email=payload.email,
            stage_all=True,
            scan_secrets=True,
        )
        # Update SurrealDB graph
        await git_graph_repo.save_commit_reference(
            project_id=project_id,
            commit_hash=commit.commit_hash,
            message=commit.message,
            author=commit.author,
            branch=commit.branch or "main",
        )
        return commit
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{project_id}/branches", response_model=List[GitBranch])
async def list_branches_api(project_id: str):
    """List local branches."""
    p_path = _get_project_path(project_id)
    return git_service.list_branches(p_path)


@router.post("/{project_id}/branches", response_model=Dict[str, str])
async def create_branch_api(project_id: str, payload: BranchRequest):
    """Create a new local branch."""
    p_path = _get_project_path(project_id)
    res = git_service.create_branch(p_path, payload.name)
    if not res.success:
        raise HTTPException(status_code=400, detail=res.stderr or res.stdout)
    return {"status": "created", "branch": payload.name}


@router.get("/{project_id}/tags", response_model=List[GitTag])
async def list_tags_api(project_id: str):
    """List project Git tags."""
    p_path = _get_project_path(project_id)
    return git_service.list_tags(p_path)


@router.post("/{project_id}/tags", response_model=GitTag)
async def create_tag_api(project_id: str, payload: TagRequest):
    """Create a Git tag."""
    p_path = _get_project_path(project_id)
    try:
        return git_service.create_tag(p_path, payload.name, message=payload.message)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{project_id}/github/init", response_model=GitHubRepository)
async def init_github_repo_api(project_id: str, payload: GitHubInitRequest):
    """Initialize remote GitHub repository, set origin, and push initial commit."""
    p_path = _get_project_path(project_id)
    try:
        gh_repo, _ = github_repo_service.initialize_github_repository(
            project_path=p_path,
            repo_name=payload.name,
            private=payload.private,
            description=payload.description or "",
            auto_push=payload.auto_push,
        )
        await git_graph_repo.save_github_repository(project_id, gh_repo)
        return gh_repo
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{project_id}/github/connect", response_model=GitHubRepository)
async def connect_github_repo_api(project_id: str, payload: GitHubConnectRequest):
    """Connect an existing GitHub repository as remote origin."""
    p_path = _get_project_path(project_id)
    try:
        gh_repo = github_repo_service.connect_existing_repository(p_path, payload.repo_spec)
        await git_graph_repo.save_github_repository(project_id, gh_repo)
        return gh_repo
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{project_id}/snapshot", response_model=ProjectSnapshot)
async def create_snapshot_api(project_id: str):
    """Create a deterministic project state snapshot linked to the current Git commit."""
    p_path = _get_project_path(project_id)
    snapshot = project_repo_manager.create_snapshot(p_path)
    await git_graph_repo.save_project_snapshot(snapshot)
    return snapshot


@router.post("/{project_id}/release", response_model=Dict[str, Any])
async def create_release_api(project_id: str, payload: ReleaseRequest):
    """Create a formal project release version, update TOON manifest, and tag Git commit."""
    p_path = _get_project_path(project_id)
    try:
        return project_repo_manager.create_release(
            project_path=p_path,
            release_version=payload.version,
            tag_message=payload.message,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
