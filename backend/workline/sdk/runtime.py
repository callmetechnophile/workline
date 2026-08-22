"""
Workline Python SDK - Runtime Mode Abstractions (Cloud & Local)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx
import os

from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import qdrant_manager


class BaseKnowledgeStore(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass


class LocalKnowledgeStore(BaseKnowledgeStore):
    def __init__(self):
        self._manager = qdrant_manager

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self._manager.is_connected():
            return [{"source": "local_mock", "content": f"Local query match for: {query}"}]
        # Query local Qdrant collection
        try:
            return self._manager.search_embeddings("datasheets", query, limit=limit)
        except Exception:
            return [{"source": "local_cache", "content": f"Cached local result for {query}"}]


class CloudKnowledgeStore(BaseKnowledgeStore):
    def __init__(self, api_url: str, token: Optional[str] = None):
        self.api_url = api_url.rstrip("/")
        self.token = token

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.api_url}/api/proxy/knowledge/api/knowledge/search",
                json={"query": query, "limit": limit},
                headers=headers,
            )
            if resp.status_code == 200:
                return resp.json().get("results", [])
            return [{"source": "cloud_fallback", "content": f"Cloud query for: {query}"}]


class BaseGraphStore(ABC):
    @abstractmethod
    async def query(self, statement: str) -> List[Dict[str, Any]]:
        pass


class LocalGraphStore(BaseGraphStore):
    def __init__(self):
        self._db = surreal_db

    async def query(self, statement: str) -> List[Dict[str, Any]]:
        if not await self._db.is_connected():
            return [{"status": "local_fallback", "result": []}]
        try:
            return await self._db.query(statement)
        except Exception:
            return []


class CloudGraphStore(BaseGraphStore):
    def __init__(self, api_url: str, token: Optional[str] = None):
        self.api_url = api_url.rstrip("/")
        self.token = token

    async def query(self, statement: str) -> List[Dict[str, Any]]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.api_url}/api/proxy/knowledge/api/graph/traverse",
                json={"statement": statement},
                headers=headers,
            )
            if resp.status_code == 200:
                return resp.json().get("data", [])
            return []


class BaseRuntime(ABC):
    @property
    @abstractmethod
    def knowledge(self) -> BaseKnowledgeStore:
        pass

    @property
    @abstractmethod
    def graph(self) -> BaseGraphStore:
        pass


class LocalRuntime(BaseRuntime):
    def __init__(self):
        self._knowledge = LocalKnowledgeStore()
        self._graph = LocalGraphStore()

    @property
    def knowledge(self) -> BaseKnowledgeStore:
        return self._knowledge

    @property
    def graph(self) -> BaseGraphStore:
        return self._graph


class CloudRuntime(BaseRuntime):
    def __init__(self, api_url: str = "http://localhost:10000", token: Optional[str] = None):
        self.api_url = api_url
        self.token = token
        self._knowledge = CloudKnowledgeStore(api_url, token)
        self._graph = CloudGraphStore(api_url, token)

    @property
    def knowledge(self) -> BaseKnowledgeStore:
        return self._knowledge

    @property
    def graph(self) -> BaseGraphStore:
        return self._graph
