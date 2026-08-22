"""Tests for hybrid retrieval combining Qdrant vectors and SurrealDB graph edges."""

import asyncio
from backend.workline.database.models import GraphEdge, GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.retrieval.embeddings import LocalEmbeddingProvider
from backend.workline.retrieval.hybrid import HybridRetriever
from backend.workline.retrieval.qdrant import COLLECTION_DOCUMENTS, QdrantManager


def test_hybrid_retrieval():
    """Test 19-21: Hybrid retrieval fusing vector similarity with SurrealDB graph context."""
    async def _run():
        embedder = LocalEmbeddingProvider(dimension=384)
        qdrant = QdrantManager(embedder=embedder)
        graph_repo = GraphRepository()

        # Seed Qdrant
        qdrant.index_document(
            collection=COLLECTION_DOCUMENTS,
            doc_id="doc_buck",
            text="LM2596 Step-Down Voltage Regulator Module 3.3V 5V Output",
            payload={"project_id": "rover"},
        )

        # Seed Graph
        p_node = GraphNode(id="project:rover", type="Project", label="Autonomous Rover", data={"project_id": "rover"})
        c_node = GraphNode(id="component:buck", type="Component", label="LM2596", data={"project_id": "rover"})
        await graph_repo.create_node(p_node)
        await graph_repo.create_node(c_node)
        await graph_repo.create_edge(
            GraphEdge(id="edge:rover_buck", source="project:rover", target="component:buck", relationship="CONTAINS")
        )

        retriever = HybridRetriever(qdrant=qdrant, graph_repo=graph_repo)
        result = await retriever.retrieve(query="voltage regulator step down", project_id="rover")

        assert len(result["documents"]) >= 1
        assert result["documents"][0]["id"] == "doc_buck"
        assert len(result["graph_relations"]["nodes"]) >= 2
        assert len(result["graph_relations"]["edges"]) >= 1

    asyncio.run(_run())
