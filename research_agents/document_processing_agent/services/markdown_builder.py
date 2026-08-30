"""
Markdown synthesizer with source page annotations (<!-- source_page: N -->) and section structure.
"""

from typing import List, Tuple
from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    ExtractedBlock,
    ExtractedSection,
    ExtractedTable,
)


class MarkdownBuilder:
    """Builds clean, structured Markdown documents annotated with page provenance."""

    def build_markdown(
        self,
        metadata: DocumentMetadata,
        blocks: List[ExtractedBlock],
        tables: List[ExtractedTable],
    ) -> Tuple[str, List[ExtractedSection]]:
        """
        Synthesizes normalized Markdown string and structured ExtractedSection list.

        Returns:
            (markdown_string, [ExtractedSection])
        """
        lines: List[str] = []
        sections: List[ExtractedSection] = []

        # 1. Title and Metadata Header
        doc_title = metadata.title or "Untitled Engineering Document"
        lines.append(f"# {doc_title}\n")

        if metadata.authors:
            lines.append(f"**Authors:** {', '.join(metadata.authors)}\n")
        if metadata.doi:
            lines.append(f"**DOI:** [{metadata.doi}](https://doi.org/{metadata.doi})\n")
        if metadata.journal or metadata.conference:
            venue = metadata.journal or metadata.conference
            lines.append(f"**Venue:** {venue}\n")

        # Group blocks by section
        section_map = {}
        for b in blocks:
            sec_name = b.section_title or "Overview"
            if sec_name not in section_map:
                section_map[sec_name] = []
            section_map[sec_name].append(b)

        last_page = -1

        for sec_title, sec_blocks in section_map.items():
            if not sec_blocks:
                continue

            page_start = sec_blocks[0].page_number
            page_end = sec_blocks[-1].page_number

            # Emit Page Provenance Comment if page changed
            if page_start != last_page:
                lines.append(f"\n<!-- source_page: {page_start} -->\n")
                last_page = page_start

            lines.append(f"## {sec_title}\n")

            sec_text_parts: List[str] = []
            for b in sec_blocks:
                if b.block_type == "heading" and b.text.strip().lower() == sec_title.lower():
                    continue  # Already emitted heading

                if b.page_number != last_page:
                    lines.append(f"\n<!-- source_page: {b.page_number} -->\n")
                    last_page = b.page_number

                if b.block_type == "code":
                    code_block = f"```\n{b.text}\n```"
                    lines.append(code_block + "\n")
                    sec_text_parts.append(code_block)
                else:
                    lines.append(b.text + "\n")
                    sec_text_parts.append(b.text)

            # Check if any tables belong to this section/page
            sec_tables = [t for t in tables if page_start <= t.page_number <= page_end]
            for tab in sec_tables:
                if tab.markdown:
                    lines.append(f"\n{tab.markdown}\n")
                    sec_text_parts.append(tab.markdown)

            sections.append(
                ExtractedSection(
                    section_title=sec_title,
                    level=2,
                    page_start=page_start,
                    page_end=page_end,
                    text="\n\n".join(sec_text_parts),
                    blocks=sec_blocks,
                )
            )

        markdown_content = "\n".join(lines).strip()
        return markdown_content, sections
