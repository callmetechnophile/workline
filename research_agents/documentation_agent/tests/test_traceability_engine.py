import pytest
from research_agents.documentation_agent.services.document_engine    import DocumentEngine
from research_agents.documentation_agent.services.traceability_engine import TraceabilityEngine
from research_agents.documentation_agent.providers.mock_provider      import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType, AuthorityLevel


def test_add_link():
    engine = DocumentEngine(MockDocProvider())
    doc    = engine.create("P1", DocumentType.TEST_PLAN, "Test Plan", "alice", {"Scope": {}})
    trace  = TraceabilityEngine()
    link   = trace.add_link(doc, "REQ-001", "verifies", authority="VERIFIED")
    assert link.target_id   == "REQ-001"
    assert link.link_type   == "verifies"
    assert link.authority   == AuthorityLevel.VERIFIED
    assert len(doc.traceability) == 1


def test_invalid_authority_falls_back_to_unknown():
    engine = DocumentEngine(MockDocProvider())
    doc    = engine.create("P1", DocumentType.TEST_PLAN, "Test Plan", "alice", {"Scope": {}})
    trace  = TraceabilityEngine()
    link   = trace.add_link(doc, "REQ-002", "satisfies", authority="SUPER_VERIFIED")
    assert link.authority == AuthorityLevel.UNKNOWN


def test_coverage_report():
    engine = DocumentEngine(MockDocProvider())
    trace  = TraceabilityEngine()
    doc1   = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    doc2   = engine.create("P1", DocumentType.TEST_PLAN, "TP", "alice", {"Scope": {}})
    trace.add_link(doc1, "REQ-1", "satisfies")
    report = trace.coverage_report([doc1, doc2])
    assert report["total_documents"] == 2
    assert report["documents_with_traceability"] == 1
    assert report["total_links"] == 1
