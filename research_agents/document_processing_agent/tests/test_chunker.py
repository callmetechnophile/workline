"""
Unit tests for semantic chunking and hierarchical subdivision.
"""

from research_agents.document_processing_agent.schemas import ExtractedBlock, ExtractedSection
from research_agents.document_processing_agent.services.chunker import SemanticChunker


def test_semantic_chunking_small_sections():
    chunker = SemanticChunker(max_tokens=200)
    sections = [
        ExtractedSection(
            section_title="Introduction",
            page_start=1,
            page_end=1,
            text="Short introduction about robotics and thermal sensors.",
            blocks=[
                ExtractedBlock(
                    block_id="b1",
                    page_number=1,
                    section_title="Introduction",
                    text="Short introduction about robotics and thermal sensors.",
                )
            ],
        ),
        ExtractedSection(
            section_title="Methodology",
            page_start=2,
            page_end=2,
            text="Methodology section describing algorithms.",
            blocks=[
                ExtractedBlock(
                    block_id="b2",
                    page_number=2,
                    section_title="Methodology",
                    text="Methodology section describing algorithms.",
                )
            ],
        ),
    ]

    chunks = chunker.chunk_document(document_id="doc_101", sections=sections)

    assert len(chunks) == 2
    assert chunks[0].section == "Introduction"
    assert chunks[0].page_start == 1
    assert chunks[1].section == "Methodology"
    assert chunks[1].page_start == 2


def test_chunking_subdivides_oversized_section():
    chunker = SemanticChunker(max_tokens=30)  # very small limit to trigger subdivision
    long_blocks = [
        ExtractedBlock(
            block_id=f"b_{i}",
            page_number=1 if i < 3 else 2,
            section_title="Long Section",
            text=f"Paragraph {i} with substantial detailed engineering text describing hardware and components.",
        )
        for i in range(6)
    ]
    section = ExtractedSection(
        section_title="Long Section",
        page_start=1,
        page_end=2,
        text="\n\n".join(b.text for b in long_blocks),
        blocks=long_blocks,
    )

    chunks = chunker.chunk_document(document_id="doc_long", sections=[section])
    assert len(chunks) > 1
    for c in chunks:
        assert c.token_estimate <= 60
