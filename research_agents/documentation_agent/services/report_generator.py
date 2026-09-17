"""
Report Generator — produces structured summary reports for document sets.
"""

from typing import Any, Dict, List

from research_agents.documentation_agent.schemas import DocumentRecord


class ReportGenerator:

    def project_doc_summary(self, docs: List[DocumentRecord]) -> Dict[str, Any]:
        by_status  = {}
        by_type    = {}
        total_links = 0
        total_flags = 0

        for doc in docs:
            s = doc.status.value
            t = doc.document_type.value
            by_status[s] = by_status.get(s, 0) + 1
            by_type[t]   = by_type.get(t, 0) + 1
            total_links  += len(doc.traceability)
            total_flags  += len(doc.quality_flags)

        return {
            "total_documents":     len(docs),
            "by_status":           by_status,
            "by_type":             by_type,
            "total_traceability_links": total_links,
            "total_quality_flags":  total_flags,
        }
