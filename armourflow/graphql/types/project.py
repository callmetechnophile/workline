"""
Project and graph exploration GraphQL types.
"""

from typing import List, Optional
import strawberry
from strawberry.scalars import JSON


@strawberry.type
class GraphNode:
    id: str
    table: str
    data: JSON


@strawberry.type
class GraphEdge:
    source: str
    relationship: str
    target: str


@strawberry.type
class EngineeringGraph:
    project_id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]


@strawberry.type
class ProjectType:
    id: str
    title: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@strawberry.type
class ProjectStatusType:
    project_id: str
    associated_tasks: int
    completed_tasks: int
    failed_tasks: int
    readiness_verdict: str
