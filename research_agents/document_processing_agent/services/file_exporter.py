"""
Local file exporter for DocumentProcessingAgent (Section 23).
Exports normalized Markdown, JSON evidence, and metadata with path traversal protection and overwrite safety.
"""

import json
from pathlib import Path
import re
from typing import Dict, List, Optional
from research_agents.document_processing_agent.schemas import DocumentProcessingOutput


class DocumentFileExporter:
    """Safely writes document markdown, full json, and metadata json to output directory."""

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitizes filename against path traversal and forbidden characters."""
        clean = re.sub(r'[<>:"/\\|?*]', '_', name.strip())
        clean = clean.strip("._ ")
        return clean or "processed_document"

    def export(
        self,
        output: DocumentProcessingOutput,
        output_dir: str,
        overwrite: bool = False,
    ) -> Dict[str, str]:
        """
        Exports [doc].md, [doc].json, and [doc].metadata.json to output_dir.

        Returns:
            Dict of {"markdown": path, "json": path, "metadata": path}
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)

        base_name = self.sanitize_filename(output.document_id or "document")
        md_file = out_path / f"{base_name}.md"
        json_file = out_path / f"{base_name}.json"
        meta_file = out_path / f"{base_name}.metadata.json"

        if not overwrite:
            for f in (md_file, json_file, meta_file):
                if f.exists():
                    raise FileExistsError(
                        f"Target export file already exists and overwrite is disabled: {f}"
                    )

        # 1. Write Markdown
        md_file.write_text(output.markdown, encoding="utf-8")

        # 2. Write Full Evidence JSON
        json_file.write_text(
            output.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # 3. Write Metadata JSON
        meta_dict = {
            "document": output.document.model_dump() if output.document else None,
            "metadata": output.metadata.model_dump() if output.metadata else None,
            "quality_score": output.quality_score,
            "quality_warnings": output.warnings,
        }
        meta_file.write_text(
            json.dumps(meta_dict, indent=2),
            encoding="utf-8",
        )

        return {
            "markdown": str(md_file),
            "json": str(json_file),
            "metadata": str(meta_file),
        }
