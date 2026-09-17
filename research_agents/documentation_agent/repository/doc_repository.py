"""
Document repository — SurrealDB-backed with in-memory dict fallback.
"""
from typing import Dict, List, Optional

from research_agents.documentation_agent.schemas import DocumentRecord


class DocRepository:

    def __init__(self):
        self._store: Dict[str, DocumentRecord] = {}
        self._db = None
        try:
            from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
            self._db = SurrealDBClient()
        except Exception:
            pass  # Use in-memory fallback

    def save(self, doc: DocumentRecord) -> None:
        self._store[doc.doc_id] = doc
        if self._db:
            try:
                self._db.upsert(f"document:{doc.doc_id}", {
                    "project_id":    doc.project_id,
                    "document_type": doc.document_type.value,
                    "title":         doc.title,
                    "status":        doc.status.value,
                    "authority":     doc.authority.value,
                    "freshness":     doc.freshness.value,
                    "revision":      doc.revision,
                    "author":        doc.author,
                })
            except Exception:
                pass

    def get(self, doc_id: str) -> Optional[DocumentRecord]:
        return self._store.get(doc_id)

    def list_by_project(self, project_id: str) -> List[DocumentRecord]:
        return [d for d in self._store.values() if d.project_id == project_id]

    def delete(self, doc_id: str) -> bool:
        return self._store.pop(doc_id, None) is not None
