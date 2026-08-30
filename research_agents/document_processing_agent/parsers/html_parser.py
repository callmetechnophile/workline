"""
BeautifulSoup-based HTML parser for DocumentProcessingAgent.
Removes navigation, cookie banners, tracking scripts, and sidebars, extracting clean
technical headings, paragraphs, lists, tables, code blocks, and links.
"""

from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
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


class HTMLDocumentParser(BaseDocumentParser):
    """Parses HTML webpages, stripping boilerplate and preserving technical hierarchy."""

    BOILERPLATE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"]
    BOILERPLATE_CLASSES = ["cookie", "ad", "sidebar", "nav", "footer", "popup", "banner", "menu"]

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
            raise CorruptedDocumentError("HTML byte content is empty.")

        try:
            html_text = content_bytes.decode("utf-8", errors="replace")
            soup = BeautifulSoup(html_text, "html.parser")
        except Exception as e:
            raise CorruptedDocumentError(f"Failed to parse HTML: {str(e)}")

        # 1. Extract Document Metadata
        title_tag = soup.find("title")
        page_title = title_tag.get_text().strip() if title_tag else (title_hint or "Web Document")

        # Meta tags
        meta_author = soup.find("meta", attrs={"name": "author"})
        authors = [meta_author["content"].strip()] if (meta_author and meta_author.get("content")) else []

        meta_date = soup.find("meta", attrs={"name": "date"}) or soup.find("meta", attrs={"property": "article:published_time"})
        pub_date = meta_date["content"].strip() if (meta_date and meta_date.get("content")) else None

        metadata = DocumentMetadata(
            title=page_title,
            authors=authors,
            publication_date=pub_date,
            page_count=1,
            document_type="html",
            file_size_bytes=len(content_bytes),
            url=source_url,
        )

        # 2. Remove Boilerplate Elements
        for tag_name in self.BOILERPLATE_TAGS:
            for el in soup.find_all(tag_name):
                el.decompose()

        for cls_name in self.BOILERPLATE_CLASSES:
            for el in soup.find_all(attrs={"class": lambda c: c and cls_name in c.lower()}):
                el.decompose()

        # 3. Extract Links
        links: List[ExtractedLink] = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            link_text = a_tag.get_text().strip() or href
            if href.startswith("http://") or href.startswith("https://"):
                l_type = "github" if "github.com" in href else ("doi" if "doi.org" in href else "web")
                links.append(
                    ExtractedLink(
                        text=link_text[:80],
                        url=href,
                        link_type=l_type,
                        page_number=1,
                    )
                )

        # 4. Extract Tables
        tables: List[ExtractedTable] = []
        for t_idx, table_el in enumerate(soup.find_all("table")):
            headers: List[str] = []
            th_tags = table_el.find_all("th")
            if th_tags:
                headers = [th.get_text().strip() for th in th_tags]

            rows: List[List[str]] = []
            for tr in table_el.find_all("tr"):
                td_tags = tr.find_all("td")
                if td_tags:
                    rows.append([td.get_text().strip() for td in td_tags])

            if headers or rows:
                if not headers and rows:
                    headers = rows[0]
                    rows = rows[1:]
                md_table = self._format_markdown_table(headers, rows)
                tables.append(
                    ExtractedTable(
                        table_id=f"tab_html_{t_idx + 1}",
                        page_number=1,
                        caption="HTML Table",
                        headers=headers,
                        rows=rows,
                        markdown=md_table,
                        extraction_status="success",
                    )
                )
            table_el.decompose()

        # 5. Extract Sequential Blocks (Headings, Paragraphs, Code)
        blocks: List[ExtractedBlock] = []
        current_section = "Overview"
        char_offset = 0
        block_counter = 0

        body = soup.find("body") or soup
        for element in body.find_all(["h1", "h2", "h3", "h4", "p", "pre", "ul", "ol"]):
            text = element.get_text().strip()
            if not text:
                continue

            tag = element.name.lower()
            if tag in ["h1", "h2", "h3", "h4"]:
                current_section = text
                b_type = "heading"
            elif tag == "pre":
                b_type = "code"
            elif tag in ["ul", "ol"]:
                b_type = "list_item"
            else:
                b_type = "paragraph"

            block_counter += 1
            b_start = char_offset
            b_end = char_offset + len(text)
            char_offset = b_end + 1

            blocks.append(
                ExtractedBlock(
                    block_id=f"b_1_{block_counter}",
                    page_number=1,
                    section_title=current_section,
                    text=text,
                    block_type=b_type,
                    character_start=b_start,
                    character_end=b_end,
                    source_url=source_url,
                )
            )

        return metadata, blocks, tables, [], links, []

    def _format_markdown_table(self, headers: List[str], rows: List[List[str]]) -> str:
        if not headers:
            return ""
        header_line = "| " + " | ".join(headers) + " |"
        sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
        row_lines = ["| " + " | ".join(r) + " |" for r in rows]
        return "\n".join([header_line, sep_line] + row_lines)
