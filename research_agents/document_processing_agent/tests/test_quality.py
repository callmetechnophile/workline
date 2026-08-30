"""
Unit tests for quality evaluation and OCR requirement detection.
"""

from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    ExtractedBlock,
    ExtractedSection,
)
from research_agents.document_processing_agent.services.quality_evaluator import QualityEvaluator


def test_quality_evaluator_high_score():
    evaluator = QualityEvaluator()
    metadata = DocumentMetadata(
        title="Valid Paper",
        authors=["Author A"],
        publication_date="2024",
        page_count=2,
        document_type="pdf",
    )
    blocks = [
        ExtractedBlock(
            block_id=f"b_{i}",
            page_number=1 if i < 3 else 2,
            text=f"Paragraph {i} containing rich technical engineering explanation with high character count.",
        )
        for i in range(6)
    ]
    sections = [
        ExtractedSection(section_title="Introduction", text="Text 1"),
        ExtractedSection(section_title="Methodology", text="Text 2"),
    ]

    status, score, warnings = evaluator.evaluate(
        metadata=metadata,
        blocks=blocks,
        sections=sections,
        tables=[],
    )

    assert status == "success"
    assert score >= 0.80


def test_quality_evaluator_triggers_ocr_required():
    evaluator = QualityEvaluator()
    metadata = DocumentMetadata(
        title="Scanned Paper",
        page_count=5,
        document_type="pdf",
    )
    # Very sparse/empty blocks typical of scanned image-only PDF
    blocks = [
        ExtractedBlock(
            block_id="b1",
            page_number=1,
            text="Scan Page",
        )
    ]

    status, score, warnings = evaluator.evaluate(
        metadata=metadata,
        blocks=blocks,
        sections=[],
        tables=[],
    )

    assert status == "ocr_required"
    assert any("OCR" in w for w in warnings)
