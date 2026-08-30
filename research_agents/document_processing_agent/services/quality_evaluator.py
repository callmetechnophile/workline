"""
Document processing quality evaluator and OCR requirement detector.
Calculates quality score (0.0 to 1.0) and emits 'ocr_required' status for scanned/flattened documents.
"""

from typing import List, Literal, Tuple
from research_agents.document_processing_agent.config import doc_config
from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    ExtractedBlock,
    ExtractedSection,
    ExtractedTable,
)


class QualityEvaluator:
    """Evaluates text richness, encoding validity, and checks if OCR is required."""

    def evaluate(
        self,
        metadata: DocumentMetadata,
        blocks: List[ExtractedBlock],
        sections: List[ExtractedSection],
        tables: List[ExtractedTable],
    ) -> Tuple[Literal["success", "ocr_required", "error"], float, List[str]]:
        """
        Evaluates extracted document artifacts.

        Returns:
            (status, quality_score, [quality_warnings])
        """
        warnings: List[str] = []
        score = 1.0

        total_text = " ".join(b.text for b in blocks)
        total_chars = len(total_text.strip())
        page_count = max(1, metadata.page_count)
        chars_per_page = total_chars / page_count

        # 1. OCR Requirement Check (Scanned / Image-only PDF)
        if metadata.document_type == "pdf":
            if total_chars < doc_config.ocr_trigger_total_chars or chars_per_page < doc_config.min_extracted_chars_per_page:
                warnings.append(
                    f"Insufficient native extractable text ({total_chars} total chars across {page_count} pages). Scanned PDF requires OCR."
                )
                return "ocr_required", 0.15, warnings

        # 2. Text Richness & Character Density
        if total_chars < 100:
            score -= 0.30
            warnings.append("Document has very short extracted text.")
        elif chars_per_page < 150:
            score -= 0.15
            warnings.append(f"Low text density detected ({chars_per_page:.1f} chars/page).")

        # 3. Metadata Completeness
        missing_meta = []
        if not metadata.title:
            missing_meta.append("title")
        if not metadata.authors:
            missing_meta.append("authors")
        if not metadata.publication_date:
            missing_meta.append("publication_date")

        if missing_meta:
            deduction = min(0.20, len(missing_meta) * 0.07)
            score -= deduction
            warnings.append(f"Incomplete document metadata (missing: {', '.join(missing_meta)}).")

        # 4. Section Detection Check
        if not sections or (len(sections) == 1 and sections[0].section_title == "Overview" and page_count > 2):
            score -= 0.15
            warnings.append("Few section boundaries detected in multi-page document.")

        # 5. Table Extraction Success
        failed_tables = [t for t in tables if t.extraction_status == "table_extraction_failed"]
        if failed_tables:
            score -= 0.10
            warnings.append(f"{len(failed_tables)} table(s) could not be parsed.")

        # 6. Encoding / Replacement Character Check
        replacement_char_count = total_text.count("\ufffd")
        if replacement_char_count > 5:
            score -= 0.15
            warnings.append(f"Detected {replacement_char_count} encoding replacement characters.")

        final_score = round(max(0.0, min(1.0, score)), 2)
        status: Literal["success", "ocr_required", "error"] = "success" if final_score >= doc_config.min_acceptable_quality_score else "error"

        return status, final_score, warnings
