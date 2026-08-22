"""Context builder pipeline for Workline ADK agents.

Retrieves authoritative project state and graph context from SurrealDB
and semantic documents from Qdrant without dumping the entire database.
"""

from typing import Any, Dict, List, Optional
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.retrieval.qdrant import COLLECTION_DOCUMENTS, QdrantManager


async def build_agent_context(
    project_id: str,
    stage: str,
    task: str,
    project_repo: Optional[ProjectRepository] = None,
    graph_repo: Optional[GraphRepository] = None,
    qdrant: Optional[QdrantManager] = None,
) -> Dict[str, Any]:
    """
    Build structured, relevant context for a specialist agent invocation.
    """
    p_repo = project_repo or ProjectRepository()
    g_repo = graph_repo or GraphRepository()
    q_mgr = qdrant or QdrantManager()

    # 1. Fetch project record from SurrealDB
    project = await p_repo.get_project(project_id)
    project_meta = {}
    bom = []
    lifecycle_stage = stage

    if project:
        project_meta = {
            "name": project.name,
            "display_name": project.display_name,
            "description": project.description,
            "domain": project.domain,
            "lifecycle_stage": project.lifecycle_stage,
            "status": project.status,
        }
        bom = project.bom
        if not lifecycle_stage:
            lifecycle_stage = project.lifecycle_stage

    # 2. Fetch relevant 1-hop / 2-hop graph relations
    graph_payload = await g_repo.get_project_graph(project_id)
    graph_summary = {
        "nodes_count": len(graph_payload.nodes),
        "edges_count": len(graph_payload.edges),
        "components": [n.label for n in graph_payload.nodes if n.type == "Component"],
        "subsystems": [n.label for n in graph_payload.nodes if n.type == "Subsystem"],
        "relationships": [
            f"{e.source} --({e.relationship})--> {e.target}" for e in graph_payload.edges[:10]
        ],
    }

    # 3. Retrieve relevant semantic documents from Qdrant
    search_query = f"{task} {stage}"
    relevant_docs = q_mgr.search(
        collection=COLLECTION_DOCUMENTS,
        query=search_query,
        limit=3,
        metadata_filter={"project_id": project_id} if project else None,
    )

    doc_summaries = [
        {"title": d.get("payload", {}).get("title", d.get("id")), "excerpt": d.get("text", "")[:200]}
        for d in relevant_docs
    ]

    return {
        "project_id": project_id,
        "current_stage": lifecycle_stage or "ideation",
        "task": task,
        "project": project_meta,
        "current_bom_count": len(bom),
        "graph_context": graph_summary,
        "relevant_documents": doc_summaries,
    }
