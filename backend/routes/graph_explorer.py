"""Graph Explorer router backed by SurrealDB Engineering Knowledge Graph."""

from fastapi import APIRouter, HTTPException, Query
from backend.armoriq.delegation import capture_plan, delegate, invoke_tool
from backend.workline.database.repositories.graph_repository import GraphRepository

router = APIRouter(prefix="/api/graph/explorer", tags=["GraphExplorer"])
graph_repo = GraphRepository()


def format_surreal_for_react_flow(graph_payload):
    """
    Ensure nodes and edges comply with React Flow format expected by GraphExplorer.tsx.
    """
    nodes = []
    edges = []

    for n in graph_payload.nodes:
        nodes.append({
            "id": n.id,
            "type": "custom" if n.type != "Project" else "input",
            "data": {
                "label": n.label,
                "type": n.type,
                **n.data,
            },
            "position": {"x": 100, "y": 100},
        })

    for e in graph_payload.edges:
        edges.append({
            "id": e.id,
            "source": e.source,
            "target": e.target,
            "label": e.relationship,
            "animated": True,
            "data": e.data,
        })

    return {"nodes": nodes, "edges": edges}


@router.get("/project/{project_id}")
async def get_project_ekg(project_id: str):
    """Fetch project engineering graph from SurrealDB."""
    try:
        # Wrap read in ArmorIQ receipt enforcer
        root_receipt = capture_plan(f"Query EKG for project {project_id}")
        graph_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["graph.read"],
            parent_receipt=root_receipt.model_dump(),
        )
        invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="graph.read",
            args={"query_name": "find_project_graph", "params": {"project_name": project_id}},
            receipt_dict=graph_receipt.model_dump(),
        )

        payload = await graph_repo.get_project_graph(project_id)
        return format_surreal_for_react_flow(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project EKG: {str(e)}")


@router.get("/component/{component_id}")
async def get_component_ekg(component_id: str):
    """Fetch component 1-hop subgraph from SurrealDB."""
    try:
        payload = await graph_repo.get_component_graph(component_id)
        return format_surreal_for_react_flow(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch component EKG: {str(e)}")


@router.get("/team/{team_id}")
async def get_team_ekg(team_id: str):
    """Fetch team subgraph from SurrealDB."""
    try:
        payload = await graph_repo.get_project_graph(team_id)
        return format_surreal_for_react_flow(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch team EKG: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_ekg(user_id: str):
    """Fetch user-associated knowledge subgraph from SurrealDB."""
    try:
        payload = await graph_repo.get_project_graph(user_id)
        return format_surreal_for_react_flow(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user EKG: {str(e)}")


@router.get("/search")
async def search_ekg(q: str = Query(..., min_length=1)):
    """Search knowledge graph in SurrealDB."""
    try:
        payload = await graph_repo.get_project_graph(q)
        return format_surreal_for_react_flow(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search EKG: {str(e)}")
