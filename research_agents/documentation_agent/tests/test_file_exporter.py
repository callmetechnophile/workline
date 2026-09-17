import pytest
from research_agents.documentation_agent.services.document_engine import DocumentEngine
from research_agents.documentation_agent.services.file_exporter   import FileExporter
from research_agents.documentation_agent.providers.mock_provider   import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType


def test_export_json():
    engine   = DocumentEngine(MockDocProvider())
    doc      = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    exporter = FileExporter()
    result   = exporter.export(doc, "json")
    assert result["format"]  == "json"
    assert result["doc_id"]  == doc.doc_id
    assert "sections" in result


def test_export_markdown():
    engine   = DocumentEngine(MockDocProvider())
    doc      = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    exporter = FileExporter()
    result   = exporter.export(doc, "markdown")
    assert result["format"]   == "markdown"
    assert "# DD" in result["content"]


def test_export_pdf_placeholder():
    engine   = DocumentEngine(MockDocProvider())
    doc      = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {})
    exporter = FileExporter()
    result   = exporter.export(doc, "pdf")
    assert result["format"]  == "pdf"
    assert result["status"]  == "EXPORT_PLACEHOLDER"
