"""
File Exporter — serializes DocumentRecord to supported export formats.
Actual PDF/DOCX rendering requires external libraries (placeholder payload returned).
"""

import json
from typing import Any, Dict

from research_agents.documentation_agent.schemas import DocumentRecord


class FileExporter:

    def export(self, doc: DocumentRecord, fmt: str) -> Dict[str, Any]:
        fmt = fmt.lower()
        if fmt == "json":
            return {
                "format":    "json",
                "doc_id":    doc.doc_id,
                "title":     doc.title,
                "status":    doc.status.value,
                "authority": doc.authority.value,
                "revision":  doc.revision,
                "sections":  doc.content_sections,
                "traceability": [
                    {"source": l.source_id, "target": l.target_id, "type": l.link_type}
                    for l in doc.traceability
                ],
            }
        elif fmt == "markdown":
            lines = [f"# {doc.title}", f"", f"**Status**: {doc.status.value}",
                     f"**Authority**: {doc.authority.value}", f"**Revision**: {doc.revision}", ""]
            for section, text in doc.content_sections.items():
                lines.append(f"## {section}")
                lines.append(text)
                lines.append("")
            return {"format": "markdown", "content": "\n".join(lines)}
        else:
            # pdf, docx, html → placeholder (requires external renderer)
            return {
                "format": fmt,
                "doc_id": doc.doc_id,
                "status": "EXPORT_PLACEHOLDER",
                "note": f"{fmt.upper()} export requires external rendering library.",
            }
