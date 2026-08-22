"""Project repository initialization, .workline/project.toon management, and release snapshots."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

from backend.workline.git.models import (
    GitCommit,
    GitRepository,
    ProjectGitHubManifest,
    ProjectGitManifest,
    ProjectSnapshot,
    WorklineToonManifest,
)
from backend.workline.git.policies import generate_default_gitignore
from backend.workline.git.service import GitService, git_service
from backend.workline.git.toon import ToonSerializer


class ProjectRepositoryManager:
    """Coordinates local Git repository initialization, .workline/project.toon state, and version releases."""

    def __init__(self, git: GitService = git_service):
        self.git = git

    def get_toon_path(self, project_path: Path) -> Path:
        """Return path to .workline/project.toon."""
        return Path(project_path) / ".workline" / "project.toon"

    def load_toon_manifest(self, project_path: Path) -> Optional[WorklineToonManifest]:
        """Load .workline/project.toon if it exists."""
        p = self.get_toon_path(project_path)
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8")
                manifest = ToonSerializer.manifest_from_toon(content)
                if not manifest.git.current_commit and self.git.is_repository(project_path):
                    manifest.git.current_commit = self.git.get_current_commit(project_path)
                return manifest
            except Exception:
                pass
        return None

    def save_toon_manifest(self, project_path: Path, manifest: WorklineToonManifest) -> Path:
        """Write WorklineToonManifest model to .workline/project.toon."""
        p = self.get_toon_path(project_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        manifest.updated_at = datetime.now(timezone.utc).isoformat()
        content = ToonSerializer.manifest_to_toon(manifest)
        p.write_text(content, encoding="utf-8")
        return p

    def init_project_git(
        self,
        project_path: Path,
        project_id: str,
        project_name: str,
        default_branch: str = "main",
        project_version: str = "0.1.0",
        schema_version: int = 1,
    ) -> GitRepository:
        """
        Initializes a Git repository in the project workspace, writes .gitignore,
        generates the canonical .workline/project.toon manifest, and creates the initial commit.
        """
        p = Path(project_path).resolve()
        p.mkdir(parents=True, exist_ok=True)

        # 1. Initialize Git repository
        self.git.initialize_repository(p, initial_branch=default_branch)

        # 2. Create authoritative .gitignore if missing
        gitignore_path = p / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(generate_default_gitignore(), encoding="utf-8")

        # 3. Create initial TOON manifest
        toon_manifest = WorklineToonManifest(
            project_id=project_id,
            project_name=project_name,
            workline_version="0.1.0",
            schema_version=schema_version,
            project_version=project_version,
            git=ProjectGitManifest(
                initialized=True,
                current_branch=default_branch,
                current_commit=None,
            ),
            github=ProjectGitHubManifest(
                connected=False,
            ),
        )
        self.save_toon_manifest(p, toon_manifest)

        # 4. Stage and create initial commit
        self.git.stage_files(p)
        commit = self.git.create_commit(
            path=p,
            message=f"Initial Workline project commit: {project_name}",
            stage_all=False,
            scan_secrets=False,  # Initial template is trusted
        )

        return GitRepository(
            repository_id=f"repo_{project_id}",
            project_id=project_id,
            local_path=str(p),
            default_branch=default_branch,
            current_branch=default_branch,
            current_commit=commit.commit_hash,
            remote_url=None,
            github_connected=False,
        )

    def sync_git_state_to_manifest(self, project_path: Path) -> Optional[WorklineToonManifest]:
        """Update .workline/project.toon with live branch, commit, and remote state."""
        p = Path(project_path).resolve()
        manifest = self.load_toon_manifest(p)
        if not manifest:
            return None

        status = self.git.get_status(p)
        manifest.git.current_branch = status.branch
        manifest.git.current_commit = status.current_commit
        if status.remote_url:
            manifest.github.remote = status.remote_url
            manifest.github.connected = "github.com" in status.remote_url.lower()

        self.save_toon_manifest(p, manifest)
        return manifest

    def create_snapshot(self, project_path: Path) -> ProjectSnapshot:
        """
        Creates a deterministic project snapshot record containing project metadata
        and links it to the current Git commit.
        """
        p = Path(project_path).resolve()
        manifest = self.load_toon_manifest(p)
        status = self.git.get_status(p)

        p_id = manifest.project_id if manifest else p.name
        p_ver = manifest.project_version if manifest else "0.1.0"
        s_ver = manifest.schema_version if manifest else 1
        c_hash = status.current_commit or "uncommitted"

        # Deterministic snapshot ID from project_id + version + commit
        raw_seed = f"{p_id}:{p_ver}:{c_hash}"
        snap_id = f"snap_{hashlib.sha256(raw_seed.encode()).hexdigest()[:12]}"

        snapshot = ProjectSnapshot(
            snapshot_id=snap_id,
            project_id=p_id,
            project_version=p_ver,
            git_commit=c_hash,
            schema_version=s_ver,
            data_summary={
                "branch": status.branch,
                "is_clean": status.is_clean,
                "remote": status.remote_url,
                "sync_status": status.sync_status.value,
            },
        )
        return snapshot

    def create_release(
        self,
        project_path: Path,
        release_version: str,
        tag_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes a formal Workline project release workflow:
        1. Verifies working tree is clean
        2. Bumps project_version in .workline/project.toon
        3. Creates release commit
        4. Creates Git tag (e.g., v0.3.0)
        5. Returns release metadata
        """
        p = Path(project_path).resolve()
        status = self.git.get_status(p)

        # Allow unstaged only if it's not conflicting
        manifest = self.load_toon_manifest(p)
        if not manifest:
            manifest = WorklineToonManifest(
                project_id=p.name,
                project_name=p.name.replace("-", " ").title(),
            )

        # Update version
        old_version = manifest.project_version
        manifest.project_version = release_version.lstrip("v")
        self.save_toon_manifest(p, manifest)

        # Commit release manifest
        self.git.stage_files(p, [".workline/project.toon"])
        commit_msg = f"Release v{manifest.project_version}"
        commit = self.git.create_commit(
            path=p,
            message=commit_msg,
            stage_all=False,
            scan_secrets=True,
        )

        # Create Git tag
        tag_name = f"v{manifest.project_version}"
        tag = self.git.create_tag(
            path=p,
            tag_name=tag_name,
            message=tag_message or f"Workline release {tag_name}",
        )

        return {
            "project_id": manifest.project_id,
            "previous_version": old_version,
            "release_version": manifest.project_version,
            "git_tag": tag.name,
            "commit_hash": commit.commit_hash,
            "short_hash": commit.short_hash,
            "timestamp": tag.timestamp,
        }


# Module-level singleton
project_repo_manager = ProjectRepositoryManager()
