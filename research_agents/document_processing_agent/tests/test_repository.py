"""
Unit tests for DocumentRepository persistence methods (Section 28).
"""

import pytest
from research_agents.document_processing_agent.repository import InMemoryDocumentRepository
from research_agents.document_processing_agent.schemas import (
    DocumentChunk,
    DocumentProcessingOutput,
    DocumentSummary,
    EngineeringEntity,
    EngineeringFact,
    ExtractedReference,
    ExtractedSection,
)


@pytest.mark.asyncio
async def test_repository_all_methods():
    repo = InMemoryDocumentRepository()

    output = DocumentProcessingOutput(
        status="success",
        document_id="doc_repo_001",
        document=DocumentSummary(
            document_id="doc_repo_001",
            title="Repository Test Document",
            document_type="pdf",
        ),
    )

    # 1. save_document
    doc_id = await repo.save_document(output)
    assert doc_id == "doc_repo_001"

    # 2. save_section
    sec_id = await repo.save_section(
        ExtractedSection(section_title="Introduction", text="Intro text"),
        document_id=doc_id,
    )
    assert "doc_repo_001" in sec_id

    # 3. save_chunk
    chunk_id = await repo.save_chunk(
        DocumentChunk(
            chunk_id="chunk_01",
            document_id=doc_id,
            text="Chunk text",
            section="Introduction",
            page_start=1,
            page_end=1,
        )
    )
    assert chunk_id == "chunk_01"

    # 4. save_entity
    ent_id = await repo.save_entity(
        EngineeringEntity(name="ESP32", category="microcontroller", page_number=1),
        document_id=doc_id,
    )
    assert "doc_repo_001" in ent_id

    # 5. save_fact
    fact_id = await repo.save_fact(
        EngineeringFact(
            fact="ESP32 operates at 3.3 V",
            entity="ESP32",
            attribute="operating_voltage",
            value="3.3 V",
            source_document=doc_id,
            page=1,
        )
    )
    assert "doc_repo_001" in fact_id

    # 6. save_reference
    ref_id = await repo.save_reference(
        ExtractedReference(reference_id="ref_1", raw_text="[1] Paper"),
        document_id=doc_id,
    )
    assert ref_id == "ref_1"

    # 7. save_document_relationship
    rel_id = await repo.save_document_relationship("doc_repo_001", "doc_repo_002", "references")
    assert "references" in rel_id

    # 8. Retrievals
    retrieved_doc = await repo.get_document(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.document_id == "doc_repo_001"
