"""
Comparison Engine — side-by-side diff of two DocumentRecord versions.
"""

from typing import Any, Dict

from research_agents.documentation_agent.schemas import DocumentRecord


class ComparisonEngine:

    def compare(self, doc_a: DocumentRecord, doc_b: DocumentRecord) -> Dict[str, Any]:
        """Return a structured comparison dict between two documents."""
        all_sections = set(doc_a.content_sections) | set(doc_b.content_sections)
        section_diffs = {}
        for section in sorted(all_sections):
            a_text = doc_a.content_sections.get(section, "[MISSING]")
            b_text = doc_b.content_sections.get(section, "[MISSING]")
            section_diffs[section] = {
                "doc_a": a_text[:200] + ("..." if len(a_text) > 200 else ""),
                "doc_b": b_text[:200] + ("..." if len(b_text) > 200 else ""),
                "changed": a_text != b_text,
            }
        return {
            "doc_a_id":      doc_a.doc_id,
            "doc_b_id":      doc_b.doc_id,
            "status_changed": doc_a.status != doc_b.status,
            "authority_changed": doc_a.authority != doc_b.authority,
            "revision_a":    doc_a.revision,
            "revision_b":    doc_b.revision,
            "section_diffs": section_diffs,
            "traceability_a": len(doc_a.traceability),
            "traceability_b": len(doc_b.traceability),
        }
