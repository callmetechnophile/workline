import pytest
from research_agents.documentation_agent.services.document_engine import DocumentEngine
from research_agents.documentation_agent.services.revision_engine import RevisionEngine
from research_agents.documentation_agent.providers.mock_provider  import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType, DocumentStatus


def test_valid_transition_draft_to_review():
    engine = DocumentEngine(MockDocProvider())
    doc    = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    rev    = RevisionEngine()
    doc, err = rev.transition(doc, DocumentStatus.IN_REVIEW, "alice", "Submitted.")
    assert err is None
    assert doc.status == DocumentStatus.IN_REVIEW


def test_invalid_transition_returns_error():
    engine = DocumentEngine(MockDocProvider())
    doc    = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    rev    = RevisionEngine()
    doc, err = rev.transition(doc, DocumentStatus.PUBLISHED, "alice", "Bad transition.")
    assert err is not None
    assert "INVALID_TRANSITION" in err


def test_self_approval_blocked():
    engine = DocumentEngine(MockDocProvider())
    doc    = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    rev    = RevisionEngine()
    doc, _ = rev.transition(doc, DocumentStatus.IN_REVIEW, "alice", "Review.")
    doc, err = rev.transition(doc, DocumentStatus.APPROVED, "alice", "Approve.", approver="alice")
    assert err is not None
    assert "SELF_APPROVAL_DENIED" in err


def test_approval_by_different_user():
    engine = DocumentEngine(MockDocProvider())
    doc    = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    rev    = RevisionEngine()
    doc, _ = rev.transition(doc, DocumentStatus.IN_REVIEW, "alice", "Review.")
    doc, err = rev.transition(doc, DocumentStatus.APPROVED, "bob", "Approve.", approver="bob")
    assert err is None
    assert doc.status == DocumentStatus.APPROVED
    assert doc.approver == "bob"
