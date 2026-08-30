"""
Unit tests for Markdown synthesis and page provenance annotations.
"""

from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    ExtractedBlock,
    ExtractedTable,
)
from research_agents.document_processing_agent.services.markdown_builder import MarkdownBuilder


def test_markdown_synthesis_with_page_annotations():
    builder = MarkdownBuilder()
    metadata = DocumentMetadata(
        title="Thermal Vision Drone Paper",
        authors=["Alice Smith"],
        doi="10.1000/182",
        page_count=2,
    )
    blocks = [
        ExtractedBlock(
            block_id="b1",
            page_number=1,
            section_title="Introduction",
            text="Autonomous drone thermal search systems locate humans.",
            block_type="paragraph",
        ),
        ExtractedBlock(
            block_id="b2",
            page_number=2,
            section_title="Methodology",
            text="We employ YOLOv8 optimized with TensorRT.",
            block_type="paragraph",
        ),
    ]
    tables = [
        ExtractedTable(
            table_id="t1",
            page_number=2,
            markdown="| Model | FPS |\n|---|---|\n| YOLOv8 | 45 |",
        )
    ]

    md_text, sections = builder.build_markdown(metadata, blocks, tables)

    assert "# Thermal Vision Drone Paper" in md_text
    assert "<!-- source_page: 1 -->" in md_text
    assert "<!-- source_page: 2 -->" in md_text
    assert "## Introduction" in md_text
    assert "## Methodology" in md_text
    assert "| Model | FPS |" in md_text
    assert len(sections) == 2
