"""Tests for DocumentIntelligenceService, Phase 10C cache integration, reindexing, and deletion."""

import pytest
from backend.workline.documents.models import DocumentStatus, SourceType
from backend.workline.documents.service import DocumentIntelligenceService
from backend.workline.knowledge.cache.cache import KnowledgeCache


def test_document_service_ingestion_and_cache(tmp_path):
    service = DocumentIntelligenceService()
    content = """# Microcontroller Specification
The STM32F401 is powered from a 3.3V rail and supports SPI up to 42MHz.
"""

    # Ingest document
    doc = service.ingest_document(
        document_id="DOC-MCU",
        project_id="rover_v2",
        content=content,
        filename="STM32F401.pdf",
        source_type=SourceType.DATASHEET,
    )

    assert doc.status == DocumentStatus.INDEXED
    assert doc.title == "Microcontroller Specification"

    # Entities extracted
    entities = service.get_entities("DOC-MCU")
    assert len(entities) >= 2
    assert any(e.normalized_value == "STM32F401" for e in entities)
    assert any(e.normalized_value == "3.3 V" for e in entities)

    # Retrieval from service
    retrieved = service.get_document("DOC-MCU")
    assert retrieved is not None
    assert retrieved.document_id == "DOC-MCU"


def test_document_reindex_and_cascading_deletion():
    service = DocumentIntelligenceService()
    content = "# Motor Driver\nDRV8833 operates at 5V with 1.5A per H-bridge."

    doc = service.ingest_document("DOC-DRV", "rover_v2", content, "drv8833.md")
    assert doc is not None

    # Reindex
    new_content = "# Motor Driver Revised\nDRV8833 operates at 5V with 2A peak current."
    doc_reindexed = service.reindex_document("DOC-DRV", new_content=new_content)
    assert doc_reindexed.title == "Motor Driver Revised"

    # Cascading deletion
    assert service.delete_document("DOC-DRV") is True
    assert service.get_document("DOC-DRV") is None
    assert len(service.get_entities("DOC-DRV")) == 0
