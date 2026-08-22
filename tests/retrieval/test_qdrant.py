"""Tests for Qdrant vector database indexing, similarity search, and embeddings."""

import pytest
from backend.workline.retrieval.embeddings import LocalEmbeddingProvider
from backend.workline.retrieval.qdrant import (
    COLLECTION_COMPONENTS,
    COLLECTION_DOCUMENTS,
    QdrantManager,
)


def test_embedding_provider():
    """Test deterministic vector embedding generation and normalization."""
    embedder = LocalEmbeddingProvider(dimension=384)
    v1 = embedder.embed_text("ESP32-S3 microcontroller datasheet")
    v2 = embedder.embed_text("ESP32-S3 microcontroller datasheet")
    v3 = embedder.embed_text("Li-ion 18650 battery cell thermal analysis")

    assert len(v1) == 384
    assert v1 == v2  # Deterministic
    assert v1 != v3  # Distinct


def test_qdrant_document_indexing_and_search():
    """Test 13-17: Document indexing, vector similarity retrieval, filtering, and deletion."""
    embedder = LocalEmbeddingProvider(dimension=384)
    qdrant = QdrantManager(embedder=embedder)

    # 1. Index documents
    qdrant.index_document(
        collection=COLLECTION_DOCUMENTS,
        doc_id="doc_esp32",
        text="ESP32-S3 Dual-Core Xtensa LX7 MCU with Wi-Fi and Bluetooth 5 LE",
        payload={"project_id": "rover", "type": "mcu", "vendor": "Espressif"},
    )
    qdrant.index_document(
        collection=COLLECTION_DOCUMENTS,
        doc_id="doc_motor_driver",
        text="DRV8833 Dual H-Bridge Motor Driver IC for DC and stepper motors",
        payload={"project_id": "rover", "type": "driver", "vendor": "TI"},
    )
    qdrant.index_document(
        collection=COLLECTION_DOCUMENTS,
        doc_id="doc_battery",
        text="Samsung 30Q 18650 3000mAh 15A Li-ion rechargeable cell",
        payload={"project_id": "drone", "type": "battery", "vendor": "Samsung"},
    )

    # 2. Search semantically
    results = qdrant.search(
        collection=COLLECTION_DOCUMENTS,
        query="microcontroller wifi bluetooth",
        limit=2,
    )
    assert len(results) >= 1
    assert results[0]["id"] == "doc_esp32"
    assert results[0]["score"] > 0.0

    # 3. Metadata filtered search
    filtered = qdrant.search(
        collection=COLLECTION_DOCUMENTS,
        query="dual motor",
        limit=5,
        metadata_filter={"project_id": "rover"},
    )
    assert len(filtered) == 2
    assert all(r["payload"]["project_id"] == "rover" for r in filtered)

    # 4. Delete document
    deleted = qdrant.delete_document(COLLECTION_DOCUMENTS, "doc_esp32")
    assert deleted is True
    post_delete = qdrant.search(COLLECTION_DOCUMENTS, "ESP32", limit=5)
    assert not any(r["id"] == "doc_esp32" for r in post_delete)
