import pytest
from research_agents.documentation_agent.services.document_engine import DocumentEngine
from research_agents.documentation_agent.providers.mock_provider  import MockDocProvider
from research_agents.documentation_agent.schemas import (
    DocumentType, DocumentStatus, AuthorityLevel,
)


def test_create_document_basic():
    engine = DocumentEngine(MockDocProvider())
    doc = engine.create(
        project_id="PROJ-1",
        document_type=DocumentType.DESIGN_DESCRIPTION,
        title="Thermal Design",
        author="eng.alice",
        section_inputs={"Scope": {}, "Background": {}},
    )
    assert doc.doc_id.startswith("DOC-")
    assert doc.project_id == "PROJ-1"
    assert doc.status     == DocumentStatus.DRAFT
    assert doc.revision   == "00"
    assert "Scope" in doc.content_sections
    assert len(doc.revision_history) == 1


def test_create_document_unknown_authority_claim():
    """Invalid authority claim must fall back to UNKNOWN, never be auto-elevated."""
    engine = DocumentEngine(MockDocProvider())
    doc = engine.create(
        project_id="P1",
        document_type=DocumentType.TEST_PLAN,
        title="Test Plan Alpha",
        author="eng.alice",
        section_inputs={"Scope": {}},
        authority_claim="INVALID_CLAIM",
    )
    assert doc.authority == AuthorityLevel.UNKNOWN


def test_create_document_assumption_not_elevated():
    engine = DocumentEngine(MockDocProvider())
    doc = engine.create(
        project_id="P1",
        document_type=DocumentType.TRADE_STUDY_REPORT,
        title="Trade Study",
        author="eng.alice",
        section_inputs={"Objective": {}},
        authority_claim="ASSUMPTION",
    )
    assert doc.authority == AuthorityLevel.ASSUMPTION


def test_update_section_bumps_revision():
    engine = DocumentEngine(MockDocProvider())
    doc = engine.create(
        project_id="P1", document_type=DocumentType.ARCHITECTURE_DOCUMENT,
        title="Arch Doc", author="eng.alice",
        section_inputs={"Scope": {"content": "initial"}},
    )
    assert doc.revision == "00"
    doc = engine.update_section(doc, "Scope", {"content": "updated"}, author="eng.bob")
    assert doc.revision == "01"
    assert len(doc.revision_history) == 2
