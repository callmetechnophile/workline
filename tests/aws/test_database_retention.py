import pytest
from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import (
    qdrant_manager,
    COLLECTION_DOCUMENTS,
    COLLECTION_COMPONENTS,
    COLLECTION_PROJECTS,
    COLLECTION_RESEARCH,
)


def test_qdrant_collections_and_search_retention():
    # Verify standard collections are registered
    assert COLLECTION_DOCUMENTS == "workline_documents"
    assert COLLECTION_COMPONENTS == "workline_components"
    assert COLLECTION_PROJECTS == "workline_projects"
    assert COLLECTION_RESEARCH == "workline_research"

    # Test indexing into memory store with cosine search
    doc_id = "doc-test-101"
    text = "Power delivery network design rules for 3.3V switching regulator"
    payload = {"source": "TI-Application-Note", "type": "power"}
    
    success = qdrant_manager.index_document(
        collection=COLLECTION_DOCUMENTS,
        doc_id=doc_id,
        text=text,
        payload=payload
    )
    assert success is True

    # Search
    results = qdrant_manager.search(
        collection=COLLECTION_DOCUMENTS,
        query="switching regulator PDN design",
        limit=2
    )
    assert len(results) > 0
    assert results[0]["id"] == doc_id
    assert results[0]["payload"]["type"] == "power"


@pytest.mark.asyncio
async def test_surrealdb_client_configuration():
    assert surreal_db.namespace is not None
    assert surreal_db.database is not None
    assert surreal_db.url is not None
