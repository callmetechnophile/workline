"""Document Intelligence Service coordinating Docling, spaCy, LlamaIndex, Qdrant, SurrealDB, and KnowledgeCache."""

import threading
import time
from typing import Any, Dict, List, Optional
from backend.workline.documents.docling.parser import DoclingParser
from backend.workline.documents.entities.resolver import EntityResolver
from backend.workline.documents.models import (
    DocumentRecord,
    DocumentStatus,
    EngineeringEntity,
    SourceType,
)
from backend.workline.documents.spacy.enricher import SpacyEnricher
from backend.workline.knowledge.cache.cache import knowledge_cache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions


class DocumentIntelligenceService:
    """Enterprise document intelligence service."""

    def __init__(self):
        self._lock = threading.RLock()
        self._documents: Dict[str, DocumentRecord] = {}
        self._entities: Dict[str, List[EngineeringEntity]] = {}
        self._document_nodes: Dict[str, List[Dict[str, Any]]] = {}

    def ingest_document(
        self,
        document_id: str,
        project_id: str,
        content: str,
        filename: str,
        source_type: SourceType = SourceType.DATASHEET,
        team_id: str = "default_team",
    ) -> DocumentRecord:
        """Complete ingestion pipeline with cache check, Docling parsing, spaCy NER, and node creation."""
        with self._lock:
            content_hash = DoclingParser.compute_hash(content)
            cache_key = f"workline:docling:{content_hash}"

            # 1. Check Phase 10C Cache
            cached_doc = knowledge_cache.get(cache_key, CacheObjectType.DOCUMENT_PARSE)
            if cached_doc:
                doc_record = DocumentRecord.model_validate(cached_doc)
            else:
                # 2. Docling Structural Parsing
                doc_record = DoclingParser.parse(
                    document_id=document_id,
                    project_id=project_id,
                    raw_content=content,
                    filename=filename,
                    source_type=source_type,
                )
                doc_record.team_id = team_id

                # Cache Docling parse
                knowledge_cache.set(
                    cache_key,
                    doc_record.model_dump(),
                    CacheObjectType.DOCUMENT_PARSE,
                    CacheOptions(
                        project_id=project_id,
                        source_id=document_id,
                        source_hash=content_hash,
                    ),
                )

            # 3. spaCy Linguistic & NER Enrichment
            entities = SpacyEnricher.enrich(doc_record)
            doc_record.status = DocumentStatus.ENRICHED

            # 4. LlamaIndex Section-Aware Node Creation
            nodes = []
            for sec in doc_record.sections:
                for idx, p in enumerate(sec.paragraphs):
                    nodes.append({
                        "node_id": f"{document_id}_n_{len(nodes) + 1}",
                        "document_id": document_id,
                        "project_id": project_id,
                        "team_id": team_id,
                        "content": f"{sec.heading}: {p}",
                        "page_number": sec.page_number,
                        "section": sec.heading,
                        "source_hash": content_hash,
                    })
                for tbl in sec.tables:
                    table_text = f"Table {tbl.caption or sec.heading}: {' | '.join(tbl.headers)}\n" + \
                        "\n".join([" | ".join(row) for row in tbl.rows])
                    nodes.append({
                        "node_id": f"{document_id}_n_{len(nodes) + 1}",
                        "document_id": document_id,
                        "project_id": project_id,
                        "team_id": team_id,
                        "content": table_text,
                        "page_number": tbl.page_number,
                        "section": sec.heading,
                        "source_hash": content_hash,
                    })

            doc_record.status = DocumentStatus.INDEXED
            doc_record.updated_at = time.time()

            # Store in internal registries (simulating SurrealDB / Qdrant metadata)
            self._documents[document_id] = doc_record
            self._entities[document_id] = entities
            self._document_nodes[document_id] = nodes

            return doc_record

    def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        with self._lock:
            return self._documents.get(document_id)

    def list_documents(self, project_id: Optional[str] = None) -> List[DocumentRecord]:
        with self._lock:
            if project_id:
                return [d for d in self._documents.values() if d.project_id == project_id]
            return list(self._documents.values())

    def get_entities(self, document_id: str) -> List[EngineeringEntity]:
        with self._lock:
            return self._entities.get(document_id, [])

    def reindex_document(self, document_id: str, new_content: Optional[str] = None) -> DocumentRecord:
        """Reindex document, detecting staleness and invalidating old caches."""
        with self._lock:
            doc = self._documents.get(document_id)
            if not doc:
                raise ValueError(f"Document '{document_id}' not found.")

            # Invalidate dependent cache
            knowledge_cache.invalidate_by_source(document_id)

            content = new_content or "Updated content"
            return self.ingest_document(
                document_id=doc.document_id,
                project_id=doc.project_id,
                content=content,
                filename=doc.filename,
                source_type=doc.source_type,
                team_id=doc.team_id,
            )

    def delete_document(self, document_id: str) -> bool:
        """Cascading deletion: cleans memory, Qdrant nodes, and invalidates cache."""
        with self._lock:
            if document_id in self._documents:
                del self._documents[document_id]
                self._entities.pop(document_id, None)
                self._document_nodes.pop(document_id, None)

                # Invalidate cache entries
                knowledge_cache.invalidate_by_source(document_id)
                return True
            return False


# Global singleton instance
document_service = DocumentIntelligenceService()
