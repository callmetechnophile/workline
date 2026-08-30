"""
Plain text and Markdown parser for DocumentProcessingAgent.
"""

import re
from typing import List, Optional, Tuple
from research_agents.document_processing_agent.parsers.base import (
    BaseDocumentParser,
    CorruptedDocumentError,
)
from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    ExtractedBlock,
    ExtractedFigure,
    ExtractedLink,
    ExtractedReference,
    ExtractedTable,
)


class TextDocumentParser(BaseDocumentParser):
    """Parses plain text and raw Markdown documents."""

    def parse(
        self,
        content_bytes: bytes,
        source_url: Optional[str] = None,
        title_hint: Optional[str] = None,
    ) -> Tuple[
        DocumentMetadata,
        List[ExtractedBlock],
        List[ExtractedTable],
        List[ExtractedFigure],
        List[ExtractedLink],
        List[ExtractedReference],
    ]:
        if not content_bytes:
            raise CorruptedDocumentError("Text document content is empty.")

        raw_text = content_bytes.decode("utf-8", errors="replace")
        normalized_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

        # Split by double newline or headers
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", normalized_text) if p.strip()]

        title = title_hint or "Text Document"
        for p in paragraphs:
            if p.startswith("# "):
                title = p.splitlines()[0].lstrip("# ").strip()
                break

        metadata = DocumentMetadata(
            title=title,
            page_count=1,
            document_type="text",
            file_size_bytes=len(content_bytes),
            url=source_url,
        )

        blocks: List[ExtractedBlock] = []
        current_section = "Overview"
        char_offset = 0
        block_counter = 0

        for p in paragraphs:
            lines = p.splitlines()
            first_line = lines[0].strip()

            if first_line.startswith("#"):
                current_section = first_line.lstrip("# ").strip()
                b_type = "heading"
                # If block only contains heading line
                if len(lines) == 1:
                    block_counter += 1
                    b_start = char_offset
                    b_end = char_offset + len(p)
                    char_offset = b_end + 1
                    blocks.append(
                        ExtractedBlock(
                            block_id=f"b_1_{block_counter}",
                            page_number=1,
                            section_title=current_section,
                            text=p,
                            block_type=b_type,
                            character_start=b_start,
                            character_end=b_end,
                            source_url=source_url,
                        )
                    )
                    continue
                else:
                    # Heading + body
                    b_body = "\n".join(lines[1:]).strip()
                    block_counter += 1
                    b_start = char_offset
                    b_end = char_offset + len(p)
                    char_offset = b_end + 1
                    blocks.append(
                        ExtractedBlock(
                            block_id=f"b_1_{block_counter}",
                            page_number=1,
                            section_title=current_section,
                            text=b_body if b_body else p,
                            block_type="paragraph",
                            character_start=b_start,
                            character_end=b_end,
                            source_url=source_url,
                        )
                    )
                    continue

            b_type = "code" if p.startswith("```") else "paragraph"
            block_counter += 1
            b_start = char_offset
            b_end = char_offset + len(p)
            char_offset = b_end + 1

            blocks.append(
                ExtractedBlock(
                    block_id=f"b_1_{block_counter}",
                    page_number=1,
                    section_title=current_section,
                    text=p,
                    block_type=b_type,
                    character_start=b_start,
                    character_end=b_end,
                    source_url=source_url,
                )
            )

        return metadata, blocks, [], [], [], []
