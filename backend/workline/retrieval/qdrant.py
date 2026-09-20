"""Qdrant vector database manager and client interface for Workline."""

import math
import os
import socket
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv
import httpx
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

from backend.workline.retrieval.embeddings import EmbeddingProvider, get_embedding_provider

# Standard Workline vector collections
COLLECTION_DOCUMENTS = "workline_documents"
COLLECTION_COMPONENTS = "workline_components"
COLLECTION_PROJECTS = "workline_projects"
COLLECTION_RESEARCH = "workline_research"


def is_port_open(url: str, timeout: float = 2.5) -> bool:
    """Fast non-blocking TCP socket check to determine if Qdrant port is open."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        if host == "localhost":
            host = "127.0.0.1"
        if parsed.port:
            port = parsed.port
        elif parsed.scheme == "https":
            port = 443
        elif parsed.scheme == "http":
            port = 80
        else:
            port = 6333
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


class QdrantManager:
    """
    Manages Qdrant vector database connections, collection lifecycle,
    vector indexing, and similarity queries with fallback in-memory cache.
    """

    def __init__(self, embedder: Optional[EmbeddingProvider] = None):
        self.url = os.environ.get("QDRANT_URL", os.environ.get("WORKLINE_QDRANT_URL", "http://127.0.0.1:6333")).rstrip("/")
        api_key_raw = os.environ.get("QDRANT_API_KEY", os.environ.get("WORKLINE_QDRANT_API_KEY"))
        if api_key_raw:
            self.api_key = api_key_raw.strip().strip("<>").strip()
        else:
            self.api_key = None
        self.embedder = embedder or get_embedding_provider()
        self.client: Optional[QdrantClient] = None

        # In-memory vector store fallback
        self._memory_points: Dict[str, Dict[str, Dict[str, Any]]] = {
            COLLECTION_DOCUMENTS: {},
            COLLECTION_COMPONENTS: {},
            COLLECTION_PROJECTS: {},
            COLLECTION_RESEARCH: {},
        }

    def connect(self) -> bool:
        """Establish client connection to Qdrant."""
        if not is_port_open(self.url):
            return False
        try:
            self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=5.0)
            return self.is_connected()
        except Exception:
            return False

    def is_connected(self) -> bool:
        """Check if Qdrant service is online and authenticated."""
        if not is_port_open(self.url):
            return False
        try:
            if self.client:
                self.client.get_collections()
                return True
            else:
                headers = {}
                if self.api_key:
                    headers["api-key"] = self.api_key
                with httpx.Client(timeout=3.0) as client:
                    res = client.get(f"{self.url}/collections", headers=headers)
                    return res.status_code == 200
        except Exception:
            return False

    def init_collections(self) -> None:
        """Ensure standard collections are provisioned."""
        if not self.client or not self.is_connected():
            return

        dim = self.embedder.get_dimension()
        standard_cols = [
            COLLECTION_DOCUMENTS,
            COLLECTION_COMPONENTS,
            COLLECTION_PROJECTS,
            COLLECTION_RESEARCH,
        ]

        for col in standard_cols:
            try:
                self.client.create_collection(
                    collection_name=col,
                    vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
                )
            except Exception:
                pass

    def index_document(
        self,
        collection: str,
        doc_id: str,
        text: str,
        payload: Dict[str, Any],
        vector: Optional[List[float]] = None,
    ) -> bool:
        """Index a document with vector and metadata."""
        vec = vector or self.embedder.embed_text(text)

        # Always update memory cache
        if collection not in self._memory_points:
            self._memory_points[collection] = {}
        self._memory_points[collection][doc_id] = {
            "id": doc_id,
            "vector": vec,
            "payload": payload,
            "text": text,
        }

        # Send to live Qdrant if online
        if self.client and self.is_connected():
            try:
                point_id = abs(hash(doc_id)) % (2**63 - 1)
                self.client.upsert(
                    collection_name=collection,
                    points=[
                        models.PointStruct(
                            id=point_id,
                            vector=vec,
                            payload={"doc_id": doc_id, "text": text, **payload},
                        )
                    ],
                )
            except Exception:
                pass

        return True

    def search(
        self,
        collection: str,
        query: str,
        limit: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for semantically similar documents.
        Queries live Qdrant HNSW index if online, else evaluates in-memory cache.
        """
        query_vec = self.embedder.embed_text(query)

        # 1. Query live Qdrant if available
        if self.client and self.is_connected():
            try:
                q_filter = None
                if metadata_filter:
                    conditions = [
                        models.FieldCondition(key=k, match=models.MatchValue(value=v))
                        for k, v in metadata_filter.items()
                    ]
                    q_filter = models.Filter(must=conditions)

                if hasattr(self.client, "query_points"):
                    res = self.client.query_points(
                        collection_name=collection,
                        query=query_vec,
                        limit=limit,
                        query_filter=q_filter,
                    )
                    points = res.points
                else:
                    points = self.client.search(
                        collection_name=collection,
                        query_vector=query_vec,
                        limit=limit,
                        query_filter=q_filter,
                    )

                results = []
                for p in points:
                    payload = getattr(p, "payload", {}) or {}
                    text_val = payload.get("text", "")
                    doc_id = payload.get("doc_id", str(p.id))
                    results.append({
                        "id": doc_id,
                        "score": round(float(p.score), 4),
                        "payload": payload,
                        "text": text_val,
                    })
                if results:
                    return results
            except Exception:
                pass

        # 2. In-memory cosine similarity search fallback
        points = self._memory_points.get(collection, {}).values()
        results = []

        for p in points:
            if metadata_filter:
                match = True
                for k, v in metadata_filter.items():
                    if p["payload"].get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            p_vec = p["vector"]
            dot_product = sum(a * b for a, b in zip(query_vec, p_vec))
            norm_a = math.sqrt(sum(a * a for a in query_vec))
            norm_b = math.sqrt(sum(b * b for b in p_vec))
            score = (dot_product / (norm_a * norm_b)) if (norm_a > 0 and norm_b > 0) else 0.0

            results.append({
                "id": p["id"],
                "score": round(score, 4),
                "payload": p["payload"],
                "text": p["text"],
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Remove a point from vector store."""
        if collection in self._memory_points and doc_id in self._memory_points[collection]:
            del self._memory_points[collection][doc_id]

        if self.client and self.is_connected():
            try:
                point_id = abs(hash(doc_id)) % (2**63 - 1)
                self.client.delete(
                    collection_name=collection,
                    points_selector=models.PointIdsList(points=[point_id]),
                )
            except Exception:
                pass
        return True


# Singleton instance
qdrant_manager = QdrantManager()
