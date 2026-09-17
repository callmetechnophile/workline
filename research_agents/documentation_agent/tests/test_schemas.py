import pytest
from research_agents.documentation_agent.schemas import (
    DocumentStatus, AuthorityLevel, DocumentFreshness,
    DocumentType, ConflictSeverity, PublicationChannel,
    DocumentRecord, TechDocInput, TechDocOutput,
)


def test_document_status_values():
    assert DocumentStatus.DRAFT.value          == "DRAFT"
    assert DocumentStatus.APPROVED.value       == "APPROVED"
    assert DocumentStatus.SUPERSEDED.value     == "SUPERSEDED"
    assert DocumentStatus.ARCHIVED.value       == "ARCHIVED"


def test_authority_levels():
    assert AuthorityLevel.AUTHORITATIVE.value  == "AUTHORITATIVE"
    assert AuthorityLevel.ASSUMPTION.value     == "ASSUMPTION"
    assert AuthorityLevel.UNKNOWN.value        == "UNKNOWN"


def test_freshness_values():
    assert DocumentFreshness.CURRENT.value     == "CURRENT"
    assert DocumentFreshness.STALE.value       == "STALE"
    assert DocumentFreshness.UNKNOWN.value     == "UNKNOWN"


def test_document_record_defaults():
    doc = DocumentRecord(
        doc_id="DOC-001", project_id="PROJ-A",
        document_type=DocumentType.FMEA_REPORT, title="Test FMEA",
    )
    assert doc.status    == DocumentStatus.DRAFT
    assert doc.authority == AuthorityLevel.UNKNOWN
    assert doc.freshness == DocumentFreshness.UNKNOWN
    assert doc.revision  == "00"
    assert doc.traceability == []


def test_input_output_defaults():
    inp = TechDocInput(project_id="P1", operation="create_document")
    assert inp.user_id    == "UNKNOWN"
    assert inp.doc_id     is None

    out = TechDocOutput(status="ok", project_id="P1", operation="create_document")
    assert out.documents  == []
    assert out.conflicts  == []
