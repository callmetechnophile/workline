"""
Unit tests for local file export (Section 23).
"""

from pathlib import Path
import tempfile
import pytest
from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    DocumentProcessingOutput,
    DocumentSummary,
)
from research_agents.document_processing_agent.services.file_exporter import DocumentFileExporter


def test_file_export_generates_md_json_and_meta():
    exporter = DocumentFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = DocumentProcessingOutput(
            status="success",
            document_id="paper_sample_123",
            document=DocumentSummary(
                document_id="paper_sample_123",
                title="Sample Paper",
                document_type="pdf",
                page_count=5,
                quality_score=0.95,
            ),
            metadata=DocumentMetadata(
                title="Sample Paper",
                authors=["Author One"],
                page_count=5,
            ),
            markdown="# Sample Paper\n\nContent here.",
        )

        paths = exporter.export(output, tmp_dir, overwrite=True)

        assert "markdown" in paths
        assert "json" in paths
        assert "metadata" in paths

        assert Path(paths["markdown"]).exists()
        assert Path(paths["json"]).exists()
        assert Path(paths["metadata"]).exists()

        assert "# Sample Paper" in Path(paths["markdown"]).read_text(encoding="utf-8")


def test_file_export_prevents_overwrite_without_flag():
    exporter = DocumentFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = DocumentProcessingOutput(
            status="success",
            document_id="paper_duplicate",
            markdown="# Test",
        )
        exporter.export(output, tmp_dir, overwrite=True)

        with pytest.raises(FileExistsError):
            exporter.export(output, tmp_dir, overwrite=False)
