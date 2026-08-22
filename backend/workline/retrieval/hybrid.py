"""Hybrid retrieval engine combining Qdrant vector search and SurrealDB graph relationships."""

from typing import Any, Dict, List, Optional
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.retrieval.qdrant import (
    COLLECTION_COMPONENTS,
    COLLECTION_DOCUMENTS,
    QdrantManager,
    qdrant_manager,
)


class HybridRetriever:
    """
    Fuses semantic similarity results from Qdrant with structured
    and relational graph context from SurrealDB.
    """

    def __init__(
        self,
        qdrant: QdrantManager = qdrant_manager,
        graph_repo: Optional[GraphRepository] = None,
    ):
        self.qdrant = qdrant
        self.graph_repo = graph_repo or GraphRepository()

    async def retrieve(
        self,
        query: str,
        project_id: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute hybrid search:
        1. Query Qdrant for relevant documents & components.
        2. Query SurrealDB for connected graph relations.
        3. Return unified context package.
        """
        filter_dict = {"project_id": project_id} if project_id else None

        # 1. Vector Search
        doc_matches = self.qdrant.search(
            collection=COLLECTION_DOCUMENTS,
            query=query,
            limit=top_k,
            metadata_filter=filter_dict,
        )

        comp_matches = self.qdrant.search(
            collection=COLLECTION_COMPONENTS,
            query=query,
            limit=top_k,
            metadata_filter=filter_dict,
        )

        # 2. Graph Traversal Context
        graph_context = None
        if project_id:
            graph_context = await self.graph_repo.get_project_graph(project_id)

        return {
            "query": query,
            "project_id": project_id,
            "documents": doc_matches,
            "components": comp_matches,
            "graph_relations": graph_context.model_dump() if graph_context else {"nodes": [], "edges": []},
        }
