import pytest
from research_agents.documentation_agent.services.document_engine  import DocumentEngine
from research_agents.documentation_agent.services.comparison_engine import ComparisonEngine
from research_agents.documentation_agent.providers.mock_provider    import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType


def test_compare_identical_documents():
    engine  = DocumentEngine(MockDocProvider())
    doc_a   = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    doc_b   = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    compare = ComparisonEngine()
    result  = compare.compare(doc_a, doc_b)
    assert "section_diffs" in result
    assert result["doc_a_id"] != result["doc_b_id"]


def test_compare_different_sections():
    engine  = DocumentEngine(MockDocProvider())
    doc_a   = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}, "Background": {}})
    doc_b   = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    compare = ComparisonEngine()
    result  = compare.compare(doc_a, doc_b)
    # Background section present in A but missing in B
    bg = result["section_diffs"].get("Background", {})
    assert bg.get("doc_b") == "[MISSING]"
