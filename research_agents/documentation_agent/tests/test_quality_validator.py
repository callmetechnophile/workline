import pytest
from research_agents.documentation_agent.services.document_engine  import DocumentEngine
from research_agents.documentation_agent.services.quality_validator import QualityValidator
from research_agents.documentation_agent.providers.mock_provider    import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType, DocumentRecord, AuthorityLevel


def test_quality_score_with_sections_and_traceability():
    engine = DocumentEngine(MockDocProvider())
    doc    = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice",
                           {"Scope": {}, "Background": {}}, authority_claim="VERIFIED")
    from research_agents.documentation_agent.services.traceability_engine import TraceabilityEngine
    TraceabilityEngine().add_link(doc, "REQ-001", "satisfies")
    validator = QualityValidator()
    score, flags = validator.validate(doc)
    # Should score above 0.75 (verified authority + traceability present)
    assert score >= 0.75
    assert all(not f.blocking for f in flags)


def test_quality_score_no_sections_is_low():
    doc = DocumentRecord(
        doc_id="DOC-TST", project_id="P1",
        document_type=DocumentType.TEST_PLAN, title="Empty Doc",
    )
    validator = QualityValidator()
    score, flags = validator.validate(doc)
    assert score < 0.60
    blocking = [f for f in flags if f.blocking]
    assert len(blocking) >= 1


def test_unknown_authority_reduces_score():
    engine    = DocumentEngine(MockDocProvider())
    doc       = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    validator = QualityValidator()
    score, flags = validator.validate(doc)
    # UNKNOWN authority should cause a flag
    flag_cats = [f.category for f in flags]
    assert "unverified_claim" in flag_cats
