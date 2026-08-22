"""Pydantic data models and graph representation models for Workline SurrealDB layer."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# 1. ENTITY MODELS
# ============================================================================

class UserModel(BaseModel):
    """User account entity."""
    id: Optional[str] = None
    name: str
    email: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TeamModel(BaseModel):
    """Collaboration team entity."""
    id: Optional[str] = None
    name: str
    uuid: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TeamMemberModel(BaseModel):
    """Team member roster entity."""
    id: Optional[str] = None
    team_id: str
    user_id: str
    email: str
    role: str = "Engineer"
    joined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class InvitationModel(BaseModel):
    """Team invitation entity."""
    id: Optional[str] = None
    team_id: str
    email: str
    role: str = "Reviewer"
    token_hash: str
    status: str = "PENDING"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProjectModel(BaseModel):
    """Authoritative project entity."""
    id: Optional[str] = None
    name: str
    display_name: str
    description: Optional[str] = ""
    domain: Optional[str] = "robotics"
    budget: Optional[Dict[str, Any]] = None
    timeline: Optional[Dict[str, Any]] = None
    complexity: Optional[str] = "medium"
    target_platform: Optional[Dict[str, Any]] = None
    current_stage: Optional[str] = "requirements"
    status: Optional[str] = "not_started"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    bom: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    power: Optional[Dict[str, Any]] = Field(default_factory=dict)
    dependencies: Optional[Dict[str, Any]] = Field(default_factory=dict)
    wiring: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    papers: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    gantt: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    code: Optional[str] = ""
    exports: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    version: Optional[int] = 1


class ProjectVersionModel(BaseModel):
    """Snapshot version of an engineering project."""
    id: Optional[str] = None
    project_id: str
    version_num: int
    data: Dict[str, Any]
    modified_by: str = "System"
    change_summary: str = "Pipeline execution"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WorkspaceBundleModel(BaseModel):
    """Serialized workspace bundle snapshot."""
    id: Optional[str] = None
    user_id: str
    name: str
    description: Optional[str] = ""
    bundle_blob: str
    checksum: str
    bundle_size: int
    field_count: int
    version: int = 1
    saved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CommentModel(BaseModel):
    """Project discussion comment."""
    id: Optional[str] = None
    project_id: str
    section: str
    author: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RequirementModel(BaseModel):
    """Engineering requirement entity."""
    id: Optional[str] = None
    project_id: str
    title: str
    description: Optional[str] = ""
    category: Optional[str] = "functional"
    priority: Optional[str] = "high"
    status: Optional[str] = "OPEN"


class SubsystemModel(BaseModel):
    """Engineering subsystem entity."""
    id: Optional[str] = None
    project_id: str
    name: str
    description: Optional[str] = ""
    status: Optional[str] = "PLANNED"


class ComponentModel(BaseModel):
    """Hardware component entity."""
    id: Optional[str] = None
    project_id: str
    name: str
    mpn: Optional[str] = ""
    manufacturer: Optional[str] = ""
    description: Optional[str] = ""
    category: Optional[str] = "MCU"
    price: Optional[float] = 0.0
    voltage: Optional[str] = "3.3V"
    current_ma: Optional[float] = 0.0
    datasheet_url: Optional[str] = ""


class DatasheetModel(BaseModel):
    """Component technical datasheet reference."""
    id: Optional[str] = None
    component_id: str
    title: str
    url: str
    verified: Optional[bool] = True


class DocumentModel(BaseModel):
    """Authoritative technical document."""
    id: Optional[str] = None
    project_id: str
    title: str
    content: str
    doc_type: Optional[str] = "datasheet"
    embedding_id: Optional[str] = None


class LifecycleStateModel(BaseModel):
    """Project lifecycle state."""
    id: Optional[str] = None
    project_id: str
    current_stage: str = "requirements"
    progress: float = 0.0
    stages: Dict[str, Any] = Field(default_factory=dict)


class GitRepositoryModel(BaseModel):
    """Git repository metadata entity in SurrealDB graph."""
    id: Optional[str] = None
    project_id: str
    remote_url: Optional[str] = None
    default_branch: str = "main"
    current_branch: str = "main"
    current_commit: Optional[str] = None
    last_sync: Optional[str] = None
    repository_visibility: str = "private"


class GitHubRepositoryModel(BaseModel):
    """Remote GitHub repository entity in SurrealDB graph."""
    id: Optional[str] = None
    owner: str
    name: str
    full_name: str
    visibility: str = "private"
    default_branch: str = "main"
    html_url: str
    clone_url: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GitCommitModel(BaseModel):
    """Git commit reference entity in SurrealDB graph."""
    id: Optional[str] = None
    commit_hash: str
    message: str
    author: str = "Workline Engineer"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    branch: str = "main"


class ProjectSnapshotModel(BaseModel):
    """Project deterministic release snapshot entity in SurrealDB graph."""
    id: Optional[str] = None
    project_id: str
    project_version: str
    git_commit: str
    schema_version: int = 1
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# 2. GRAPH INTERCHANGE MODELS
# ============================================================================

class GraphNode(BaseModel):
    """Node in the engineering knowledge graph."""
    id: str
    type: str
    label: str
    data: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Directed relationship edge between nodes."""
    id: str
    source: str = ""
    target: str = ""
    relationship: str
    data: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        if "source_id" in data and not data.get("source"):
            data["source"] = data.pop("source_id")
        if "target_id" in data and not data.get("target"):
            data["target"] = data.pop("target_id")
        super().__init__(**data)


class GraphPayload(BaseModel):
    """Full graph network payload for frontend graph explorers."""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
