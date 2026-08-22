"""FastAPI router for Engineering Knowledge Graph exploration."""

from typing import Optional
from fastapi import APIRouter, Query
from backend.workline.database.models import GraphPayload
from backend.workline.database.repositories.graph_repository import GraphRepository

router = APIRouter(prefix="/api/graph", tags=["Engineering Graph"])
graph_repo = GraphRepository()


@router.get("/project/{project_id}", response_model=GraphPayload)
async def get_project_graph(project_id: str):
    """Retrieve complete engineering graph for a project."""
    return await graph_repo.get_project_graph(project_id)


@router.get("/component/{component_id}", response_model=GraphPayload)
async def get_component_graph(component_id: str):
    """Retrieve 1-hop subgraph centered on a component."""
    return await graph_repo.get_component_graph(component_id)


@router.get("/subsystem/{subsystem_id}", response_model=GraphPayload)
async def get_subsystem_graph(subsystem_id: str):
    """Retrieve subgraph for a specific subsystem."""
    return await graph_repo.get_subsystem_graph(subsystem_id)


@router.get("/path", response_model=GraphPayload)
async def get_path_graph(
    source_id: str = Query(..., description="Source node identifier"),
    target_id: str = Query(..., description="Target node identifier"),
):
    """Find directed path between two entities in the knowledge graph."""
    return await graph_repo.get_path_graph(source_id, target_id)
