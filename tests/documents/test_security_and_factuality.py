"""Tests for security isolation and no-hallucination factuality checks."""

import pytest
from backend.workline.documents.models import SourceType
from backend.workline.documents.service import DocumentIntelligenceService


def test_project_and_team_isolation():
    service = DocumentIntelligenceService()

    service.ingest_document(
        document_id="DOC-PROJ-A",
        project_id="proj_A",
        content="Secret Project A spec",
        filename="specA.md",
        team_id="team_alpha",
    )

    service.ingest_document(
        document_id="DOC-PROJ-B",
        project_id="proj_B",
        content="Project B spec",
        filename="specB.md",
        team_id="team_beta",
    )

    docs_a = service.list_documents("proj_A")
    docs_b = service.list_documents("proj_B")

    assert len(docs_a) == 1
    assert docs_a[0].document_id == "DOC-PROJ-A"

    assert len(docs_b) == 1
    assert docs_b[0].document_id == "DOC-PROJ-B"


def test_factuality_no_hallucination():
    service = DocumentIntelligenceService()
    content = """# Step Down Converter
The device supports maximum output current of 3A.
The input supply voltage range is 3V to 17V.
"""
    doc = service.ingest_document("DOC-FACT", "rover_v2", content, "fact_check.md")
    entities = service.get_entities("DOC-FACT")

    curr_entities = [e for e in entities if e.entity_type == "CURRENT"]
    assert len(curr_entities) == 1
    assert curr_entities[0].normalized_value == "3 A"
    # Ensure source span faithfully captures the exact context
    assert "maximum output current of 3A" in curr_entities[0].source_span
    assert "maximum input current" not in curr_entities[0].source_span
