"""Docling structural parser extracting sections, tables, paragraphs, and page provenance."""

import hashlib
import time
from typing import List
from backend.workline.documents.models import (
    DocumentRecord,
    DocumentStatus,
    SectionElement,
    SourceType,
    TableElement,
)


class DoclingParser:
    """Parses raw text/markdown/PDF into hierarchical sections and structured tables."""

    @classmethod
    def compute_hash(cls, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def parse(
        cls,
        document_id: str,
        project_id: str,
        raw_content: str,
        filename: str,
        source_type: SourceType = SourceType.DATASHEET,
    ) -> DocumentRecord:
        content_hash = cls.compute_hash(raw_content)
        lines = raw_content.splitlines()
        sections: List[SectionElement] = []

        current_sec = SectionElement(
            section_id=f"{document_id}_sec_0",
            heading="General Overview",
            level=1,
            page_number=1,
            paragraphs=[],
            tables=[],
            figures=[],
        )

        p_buffer = []
        page = 1
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                if p_buffer:
                    current_sec.paragraphs.append(" ".join(p_buffer))
                    p_buffer = []
                i += 1
                continue

            if line.lower().startswith("page ") or line.startswith("--- Page"):
                page += 1
                i += 1
                continue

            # Table detection (markdown tables | col1 | col2 |)
            if line.startswith("|") and line.endswith("|"):
                if p_buffer:
                    current_sec.paragraphs.append(" ".join(p_buffer))
                    p_buffer = []

                table_rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    row_str = lines[i].strip()
                    if "---" not in row_str:
                        cols = [c.strip() for c in row_str.split("|")[1:-1]]
                        table_rows.append(cols)
                    i += 1

                if table_rows:
                    headers = table_rows[0]
                    rows = table_rows[1:]
                    tbl = TableElement(
                        table_id=f"{document_id}_tbl_{len(current_sec.tables) + 1}",
                        document_id=document_id,
                        page_number=page,
                        section_title=current_sec.heading,
                        headers=headers,
                        rows=rows,
                        caption=f"Table in {current_sec.heading}",
                    )
                    current_sec.tables.append(tbl)
                continue

            # Heading detection
            if line.startswith("#") or (line.isupper() and 3 < len(line) < 60):
                if p_buffer:
                    current_sec.paragraphs.append(" ".join(p_buffer))
                    p_buffer = []

                if current_sec.paragraphs or current_sec.tables:
                    sections.append(current_sec)

                heading_text = line.lstrip("#").strip()
                current_sec = SectionElement(
                    section_id=f"{document_id}_sec_{len(sections) + 1}",
                    heading=heading_text,
                    level=2 if line.startswith("##") else 1,
                    page_number=page,
                    paragraphs=[],
                    tables=[],
                    figures=[],
                )
                i += 1
                continue

            p_buffer.append(line)
            i += 1

        if p_buffer:
            current_sec.paragraphs.append(" ".join(p_buffer))
        sections.append(current_sec)

        title = sections[0].heading if sections else filename

        return DocumentRecord(
            document_id=document_id,
            project_id=project_id,
            team_id="default_team",
            source_type=source_type,
            source_uri=f"file://{filename}",
            filename=filename,
            mime_type="application/pdf" if filename.endswith(".pdf") else "text/markdown",
            title=title,
            source_hash=content_hash,
            content_hash=content_hash,
            created_at=time.time(),
            updated_at=time.time(),
            parser="DoclingParser",
            parser_version="2.1.0",
            status=DocumentStatus.PARSED,
            sections=sections,
            metadata={"page_count": page},
        )
