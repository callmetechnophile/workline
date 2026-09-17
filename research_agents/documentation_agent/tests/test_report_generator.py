import pytest
from research_agents.documentation_agent.services.document_engine  import DocumentEngine
from research_agents.documentation_agent.services.report_generator import ReportGenerator
from research_agents.documentation_agent.providers.mock_provider    import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType


def test_project_doc_summary():
    engine = DocumentEngine(MockDocProvider())
    docs   = [
        engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}}),
        engine.create("P1", DocumentType.FMEA_REPORT, "FMEA", "alice", {"Scope": {}}),
    ]
    reporter = ReportGenerator()
    report   = reporter.project_doc_summary(docs)
    assert report["total_documents"] == 2
    assert "DRAFT" in report["by_status"]
    assert DocumentType.FMEA_REPORT.value in report["by_type"]
