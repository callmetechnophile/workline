"""
Traceability Engine — manages requirement-to-verification links.
All link metadata is deterministic; LLM is not involved here.
"""

import uuid
from typing import List, Optional

from research_agents.documentation_agent.schemas import (
    AuthorityLevel, DocumentRecord, TraceabilityLink,
)


class TraceabilityEngine:

    def add_link(
        self,
        doc: DocumentRecord,
        target_id: str,
        link_type: str,
        authority: Optional[str] = None,
    ) -> TraceabilityLink:
        """Attach a traceability link to a document record."""
        auth = AuthorityLevel.UNKNOWN
        if authority:
            try:
                auth = AuthorityLevel(authority.upper())
            except ValueError:
                auth = AuthorityLevel.UNKNOWN  # Never silently elevate

        link = TraceabilityLink(
            source_id=doc.doc_id,
            target_id=target_id,
            link_type=link_type,
            authority=auth,
        )
        doc.traceability.append(link)
        return link

    def get_links(self, doc: DocumentRecord) -> List[TraceabilityLink]:
        return list(doc.traceability)

    def coverage_report(self, docs: List[DocumentRecord]) -> dict:
        """Return traceability coverage metrics across a list of documents."""
        total_links   = sum(len(d.traceability) for d in docs)
        docs_with_links = sum(1 for d in docs if d.traceability)
        return {
            "total_documents": len(docs),
            "documents_with_traceability": docs_with_links,
            "total_links": total_links,
            "coverage_pct": (docs_with_links / max(len(docs), 1)) * 100,
        }
