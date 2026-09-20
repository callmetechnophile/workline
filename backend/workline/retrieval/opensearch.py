"""
Amazon OpenSearch Service client adapter for Workline / ArmourFlow platform.
Enables full-text indexing and semantic search across:
- Research papers & summaries
- Component specifications & datasheets
- Engineering decisions & project design records

Note: Operates strictly as a search/index layer.
SurrealDB remains authoritative for relationships and graph topology.
Qdrant remains authoritative for ANN vector embeddings.
"""

import os
from typing import Any, Dict, List, Optional
from loguru import logger


class OpenSearchIndexManager:
    """
    Manages indexing and search queries against Amazon OpenSearch Service.
    Falls back gracefully to local text matching when OpenSearch is offline.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        self.endpoint = endpoint or os.environ.get("OPENSEARCH_ENDPOINT")
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self._client = None
        self._local_docs: Dict[str, List[Dict[str, Any]]] = {
            "workline_papers": [],
            "workline_components": [],
            "workline_projects": [],
        }
        self._init_client()

    def _init_client(self):
        if not self.endpoint:
            logger.info("[OpenSearch] OPENSEARCH_ENDPOINT not set; operating on local in-memory index.")
            return

        try:
            from opensearchpy import OpenSearch, RequestsHttpConnection
            from requests_aws4auth import AWS4Auth
            import boto3

            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                self.region_name,
                "es",
                session_token=credentials.token,
            )

            self._client = OpenSearch(
                hosts=[{"host": self.endpoint.replace("https://", "").replace("http://", ""), "port": 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
            )
            logger.info(f"[OpenSearch] Connected to OpenSearch cluster at {self.endpoint}")
        except Exception as e:
            logger.warning(f"[OpenSearch] Could not initialize OpenSearch client ({e}); local fallback active.")
            self._client = None

    async def index_document(self, index_name: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index a document in OpenSearch or local storage."""
        if index_name not in self._local_docs:
            self._local_docs[index_name] = []

        # Update local cache
        self._local_docs[index_name] = [d for d in self._local_docs[index_name] if d.get("id") != doc_id]
        self._local_docs[index_name].append({"id": doc_id, **document})

        if not self._client:
            return True

        try:
            self._client.index(index=index_name, id=doc_id, body=document, refresh=True)
            return True
        except Exception as e:
            logger.warning(f"[OpenSearch] index_document failed ({e})")
            return False

    async def search_documents(self, index_name: str, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by keyword query."""
        if not self._client:
            # Fallback simple substring search
            matches = []
            q = query_text.lower()
            for doc in self._local_docs.get(index_name, []):
                doc_str = " ".join(str(v) for v in doc.values()).lower()
                if q in doc_str:
                    matches.append(doc)
                if len(matches) >= limit:
                    break
            return matches

        try:
            query = {
                "size": limit,
                "query": {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["title^2", "content", "abstract", "description", "part_number^3"],
                    }
                },
            }
            resp = self._client.search(index=index_name, body=query)
            hits = resp.get("hits", {}).get("hits", [])
            return [{"id": h["_id"], **h["_source"]} for h in hits]
        except Exception as e:
            logger.warning(f"[OpenSearch] search failed ({e})")
            return []


# Global singleton instance
opensearch_manager = OpenSearchIndexManager()
