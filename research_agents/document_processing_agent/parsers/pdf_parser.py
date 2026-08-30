"""
PyMuPDF-based page-aware PDF parser for DocumentProcessingAgent.
Extracts layout blocks, headings, paragraphs, tables, figures, links, and metadata
while strictly preserving page boundaries.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
import pymupdf as fitz
from loguru import logger

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


class PDFDocumentParser(BaseDocumentParser):
    """Parses PDF documents using PyMuPDF with layout and page boundary preservation."""

    HEADING_REGEX = re.compile(
        r"^((\d+(\.\d+)*\s+)?([A-Z][A-Za-z0-9\s-]{2,60}))\s*$"
    )
    FIGURE_REGEX = re.compile(r"^(Figure|Fig\.)\s*(\d+[a-zA-Z]?)\s*[:.-]\s*(.+)", re.IGNORECASE)
    TABLE_REGEX = re.compile(r"^(Table|Tab\.)\s*(\d+[a-zA-Z]?)\s*[:.-]\s*(.+)", re.IGNORECASE)

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
            raise CorruptedDocumentError("PDF byte content is empty.")

        try:
            doc = fitz.open(stream=content_bytes, filetype="pdf")
        except Exception as e:
            raise CorruptedDocumentError(f"Failed to open PDF with PyMuPDF: {str(e)}")

        page_count = len(doc)
        if page_count == 0:
            raise CorruptedDocumentError("PDF contains 0 pages.")

        # Extract Document Metadata
        raw_meta = doc.metadata or {}
        title = raw_meta.get("title") or title_hint
        authors_raw = raw_meta.get("author")
        authors = [a.strip() for a in authors_raw.split(";") if a.strip()] if authors_raw else []

        metadata = DocumentMetadata(
            title=title,
            authors=authors,
            publication_date=raw_meta.get("creationDate"),
            publisher=raw_meta.get("producer") or raw_meta.get("creator"),
            page_count=page_count,
            document_type="pdf",
            file_size_bytes=len(content_bytes),
            creation_date=raw_meta.get("creationDate"),
            modification_date=raw_meta.get("modDate"),
            url=source_url,
            pdf_url=source_url if (source_url and source_url.lower().endswith(".pdf")) else None,
        )

        blocks: List[ExtractedBlock] = []
        tables: List[ExtractedTable] = []
        figures: List[ExtractedFigure] = []
        links: List[ExtractedLink] = []
        references: List[ExtractedReference] = []

        current_section = "Abstract" if page_count > 1 else "Introduction"
        char_offset = 0
        block_counter = 0
        is_references_section = False

        for page_idx in range(page_count):
            page_num = page_idx + 1
            page = doc[page_idx]

            # 1. Extract Links from Page
            page_links = page.get_links()
            for pl in page_links:
                uri = pl.get("uri")
                if uri:
                    link_type = "doi" if "doi.org" in uri else ("github" if "github.com" in uri else "web")
                    links.append(
                        ExtractedLink(
                            text=uri,
                            url=uri,
                            link_type=link_type,
                            page_number=page_num,
                        )
                    )

            # 2. Extract Native Tables if available in PyMuPDF
            try:
                native_tables = page.find_tables()
                if native_tables and hasattr(native_tables, "tables"):
                    for t_idx, tab in enumerate(native_tables.tables):
                        extracted_rows = tab.extract()
                        if extracted_rows and len(extracted_rows) >= 2:
                            headers = [str(c or "").strip() for c in extracted_rows[0]]
                            rows = [[str(c or "").strip() for c in r] for r in extracted_rows[1:]]
                            md_table = self._format_markdown_table(headers, rows)
                            tables.append(
                                ExtractedTable(
                                    table_id=f"tab_p{page_num}_{t_idx + 1}",
                                    page_number=page_num,
                                    caption=f"Table on page {page_num}",
                                    headers=headers,
                                    rows=rows,
                                    markdown=md_table,
                                    extraction_status="success",
                                )
                            )
            except Exception as tab_err:
                logger.debug(f"Native table extraction skipped on page {page_num}: {tab_err}")

            # 3. Extract Text Blocks
            page_blocks = page.get_text("blocks")
            for b in page_blocks:
                # b format: (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) < 5:
                    continue
                raw_text = b[4].strip()
                if not raw_text:
                    continue

                # Filter repeated page headers / footers
                y0, y1 = b[1], b[3]
                if (y0 < 30 and page_num > 1) or (y1 > page.rect.height - 30 and len(raw_text) < 50):
                    # Likely running header or page number footer
                    continue

                # Detect Section Headings
                if self._is_heading_block(raw_text):
                    current_section = self._clean_heading(raw_text)
                    if "reference" in current_section.lower() or "bibliography" in current_section.lower():
                        is_references_section = True

                # Detect Figures
                fig_match = self.FIGURE_REGEX.match(raw_text)
                if fig_match:
                    figures.append(
                        ExtractedFigure(
                            figure_number=fig_match.group(2),
                            caption=fig_match.group(3).strip(),
                            page_number=page_num,
                            bounding_box=[b[0], b[1], b[2], b[3]],
                        )
                    )

                # Process References
                if is_references_section and raw_text != current_section:
                    ref_items = self._parse_reference_block(raw_text)
                    references.extend(ref_items)

                # Append Block
                block_counter += 1
                b_start = char_offset
                b_end = char_offset + len(raw_text)
                char_offset = b_end + 1

                block_type = "heading" if self._is_heading_block(raw_text) else ("code" if "```" in raw_text else "paragraph")

                blocks.append(
                    ExtractedBlock(
                        block_id=f"b_{page_num}_{block_counter}",
                        page_number=page_num,
                        section_title=current_section,
                        text=raw_text,
                        block_type=block_type,
                        character_start=b_start,
                        character_end=b_end,
                        source_url=source_url,
                    )
                )

        doc.close()
        return metadata, blocks, tables, figures, links, references

    def _is_heading_block(self, text: str) -> bool:
        """Determines if a short text block represents a section header."""
        lines = text.splitlines()
        if len(lines) > 2 or len(text) > 80:
            return False
        first_line = lines[0].strip()
        common_sections = {
            "abstract", "introduction", "background", "related work", "methodology",
            "system architecture", "hardware design", "implementation", "experiments",
            "experimental results", "results", "discussion", "conclusion",
            "future work", "references", "bibliography", "acknowledgments",
        }
        if first_line.lower().rstrip(":") in common_sections:
            return True
        return bool(self.HEADING_REGEX.match(first_line))

    def _clean_heading(self, text: str) -> str:
        first_line = text.splitlines()[0].strip()
        return re.sub(r"^\d+(\.\d+)*\s*", "", first_line).strip()

    def _format_markdown_table(self, headers: List[str], rows: List[List[str]]) -> str:
        if not headers:
            return ""
        header_line = "| " + " | ".join(headers) + " |"
        sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
        row_lines = ["| " + " | ".join(r) + " |" for r in rows]
        return "\n".join([header_line, sep_line] + row_lines)

    def _parse_reference_block(self, text: str) -> List[ExtractedReference]:
        refs: List[ExtractedReference] = []
        entries = re.split(r"(?:^|\n)\[(\d+)\]\s*", text)
        if len(entries) > 1:
            for i in range(1, len(entries), 2):
                ref_num = entries[i]
                ref_text = entries[i + 1].strip() if i + 1 < len(entries) else ""
                year_match = re.search(r"\b(19\d\d|20\d\d)\b", ref_text)
                doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", ref_text)
                doi_str = doi_match.group(0).rstrip(".,;") if doi_match else None
                refs.append(
                    ExtractedReference(
                        reference_id=f"ref_{ref_num}",
                        raw_text=f"[{ref_num}] {ref_text}",
                        title=ref_text[:100],
                        year=int(year_match.group(1)) if year_match else None,
                        doi=doi_str,
                    )
                )
        else:
            refs.append(
                ExtractedReference(
                    reference_id=f"ref_{abs(hash(text)) % 10000}",
                    raw_text=text,
                    title=text[:100],
                )
            )
        return refs
