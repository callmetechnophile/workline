"""SurrealDB graph persistence for Git repository, commit, and GitHub remote metadata."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.workline.database.models import (
    GitCommitModel,
    GitHubRepositoryModel,
    GitRepositoryModel,
    ProjectSnapshotModel,
)
from backend.workline.database.surrealdb import SurrealDBManager, surreal_db
from backend.workline.git.models import GitHubRepository, GitRepository, ProjectSnapshot


class GitGraphRepository:
    """Stores Git versioning, repository, and snapshot references in the SurrealDB graph."""

    def __init__(self, db: SurrealDBManager = surreal_db):
        self.db = db
        # In-memory storage for offline / testing execution
        self._repositories: Dict[str, GitRepositoryModel] = {}
        self._github_repos: Dict[str, GitHubRepositoryModel] = {}
        self._commits: Dict[str, GitCommitModel] = {}
        self._snapshots: Dict[str, ProjectSnapshotModel] = {}
        self._edges: List[Dict[str, Any]] = []

    async def save_git_repository(self, repo: GitRepository) -> GitRepositoryModel:
        """Persist Git repository metadata and link Project -[HAS_REPOSITORY]-> GitRepository."""
        repo_id = f"git_repo:{repo.project_id}"
        model = GitRepositoryModel(
            id=repo_id,
            project_id=repo.project_id,
            remote_url=repo.remote_url,
            default_branch=repo.default_branch,
            current_branch=repo.current_branch,
            current_commit=repo.current_commit,
            last_sync=repo.last_sync or datetime.now(timezone.utc).isoformat(),
            repository_visibility=repo.visibility.value,
        )
        self._repositories[repo_id] = model
        self._repositories[repo.project_id] = model

        # Edge: Project -> GitRepository
        self._edges.append({
            "source": f"project:{repo.project_id}",
            "target": repo_id,
            "relationship": "HAS_REPOSITORY",
        })

        if await self.db.is_connected():
            try:
                data = model.model_dump()
                sql = f"UPSERT {repo_id} CONTENT $data;"
                await self.db.query(sql, {"data": data})
                edge_sql = f"RELATE project:{repo.project_id}->HAS_REPOSITORY->{repo_id};"
                await self.db.query(edge_sql)
            except Exception:
                pass

        return model

    async def save_github_repository(self, project_id: str, gh_repo: GitHubRepository) -> GitHubRepositoryModel:
        """Persist remote GitHub repository and link GitRepository -[HAS_REMOTE]-> GitHubRepository."""
        gh_id = f"github_repo:{gh_repo.owner}_{gh_repo.name}"
        model = GitHubRepositoryModel(
            id=gh_id,
            owner=gh_repo.owner,
            name=gh_repo.name,
            full_name=gh_repo.full_name,
            visibility=gh_repo.visibility.value,
            default_branch=gh_repo.default_branch,
            html_url=gh_repo.html_url,
            clone_url=gh_repo.clone_url,
            created_at=gh_repo.created_at,
            updated_at=gh_repo.updated_at,
        )
        self._github_repos[gh_id] = model
        self._github_repos[project_id] = model

        repo_id = f"git_repo:{project_id}"
        self._edges.append({
            "source": repo_id,
            "target": gh_id,
            "relationship": "HAS_REMOTE",
        })

        if await self.db.is_connected():
            try:
                data = model.model_dump()
                sql = f"UPSERT {gh_id} CONTENT $data;"
                await self.db.query(sql, {"data": data})
                edge_sql = f"RELATE {repo_id}->HAS_REMOTE->{gh_id};"
                await self.db.query(edge_sql)
            except Exception:
                pass

        return model

    async def save_commit_reference(
        self,
        project_id: str,
        commit_hash: str,
        message: str,
        author: str = "Workline Engineer",
        branch: str = "main",
    ) -> GitCommitModel:
        """Persist current commit reference and link GitRepository -[CURRENT_VERSION]-> GitCommit."""
        commit_id = f"git_commit:{commit_hash[:12]}"
        model = GitCommitModel(
            id=commit_id,
            commit_hash=commit_hash,
            message=message,
            author=author,
            branch=branch,
        )
        self._commits[commit_id] = model
        self._commits[commit_hash] = model

        repo_id = f"git_repo:{project_id}"
        self._edges.append({
            "source": repo_id,
            "target": commit_id,
            "relationship": "CURRENT_VERSION",
        })

        if await self.db.is_connected():
            try:
                data = model.model_dump()
                sql = f"UPSERT {commit_id} CONTENT $data;"
                await self.db.query(sql, {"data": data})
                edge_sql = f"RELATE {repo_id}->CURRENT_VERSION->{commit_id};"
                await self.db.query(edge_sql)
            except Exception:
                pass

        return model

    async def save_project_snapshot(self, snapshot: ProjectSnapshot) -> ProjectSnapshotModel:
        """Persist a deterministic project snapshot."""
        snap_id = f"snapshot:{snapshot.snapshot_id}"
        model = ProjectSnapshotModel(
            id=snap_id,
            project_id=snapshot.project_id,
            project_version=snapshot.project_version,
            git_commit=snapshot.git_commit,
            schema_version=snapshot.schema_version,
            timestamp=snapshot.timestamp,
        )
        self._snapshots[snap_id] = model
        self._snapshots[snapshot.snapshot_id] = model

        if await self.db.is_connected():
            try:
                data = model.model_dump()
                sql = f"UPSERT {snap_id} CONTENT $data;"
                await self.db.query(sql, {"data": data})
            except Exception:
                pass

        return model

    async def get_git_repository(self, project_id: str) -> Optional[GitRepositoryModel]:
        """Fetch Git repository metadata for a project."""
        repo_id = f"git_repo:{project_id}"
        if await self.db.is_connected():
            try:
                sql = f"SELECT * FROM {repo_id};"
                res = await self.db.query(sql)
                if res and isinstance(res, list) and len(res) > 0:
                    item = res[0]
                    if isinstance(item, dict) and "result" in item:
                        item = item["result"]
                    if isinstance(item, list) and len(item) > 0:
                        return GitRepositoryModel.model_validate(item[0])
                    elif isinstance(item, dict):
                        return GitRepositoryModel.model_validate(item)
            except Exception:
                pass
        return self._repositories.get(repo_id) or self._repositories.get(project_id)

    async def get_github_repository(self, project_id: str) -> Optional[GitHubRepositoryModel]:
        """Fetch GitHub repository metadata for a project."""
        if await self.db.is_connected():
            try:
                sql = f"SELECT ->HAS_REMOTE->github_repo.* FROM git_repo:{project_id};"
                res = await self.db.query(sql)
                if res and isinstance(res, list) and len(res) > 0:
                    item = res[0]
                    if isinstance(item, dict) and "result" in item:
                        item = item["result"]
                    if isinstance(item, list) and len(item) > 0:
                        return GitHubRepositoryModel.model_validate(item[0])
            except Exception:
                pass
        return self._github_repos.get(project_id)


# Module-level singleton
git_graph_repo = GitGraphRepository()
