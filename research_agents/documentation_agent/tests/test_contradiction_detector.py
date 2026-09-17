import pytest
from research_agents.documentation_agent.services.document_engine      import DocumentEngine
from research_agents.documentation_agent.services.contradiction_detector import ContradictionDetector
from research_agents.documentation_agent.providers.mock_provider        import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType


def test_no_conflicts_for_distinct_documents():
    engine = DocumentEngine(MockDocProvider())
    doc_a  = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "Design Doc", "alice", {"Scope": {}})
    doc_b  = engine.create("P1", DocumentType.FMEA_REPORT, "FMEA", "bob", {"Scope": {}})
    detector = ContradictionDetector()
    conflicts = detector.detect(doc_a, doc_b)
    # Different types, different titles → no duplicate conflict (authority gap may vary)
    dup_conflicts = [c for c in conflicts if "title" in c.field]
    assert len(dup_conflicts) == 0


def test_duplicate_type_title_conflict():
    engine   = DocumentEngine(MockDocProvider())
    doc_a    = engine.create("P1", DocumentType.FMEA_REPORT, "Same Title", "alice", {"Scope": {}})
    doc_b    = engine.create("P1", DocumentType.FMEA_REPORT, "Same Title", "bob",   {"Scope": {}})
    detector = ContradictionDetector()
    conflicts = detector.detect(doc_a, doc_b)
    dup = [c for c in conflicts if "title" in c.field]
    assert len(dup) >= 1
    # Resolution must always be CONFLICT_DETECTED — never auto-resolved
    assert all(c.resolution == "CONFLICT_DETECTED" for c in conflicts)
