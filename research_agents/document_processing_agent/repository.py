"""
Repository interface for processed document, markdown, chunk, and fact storage (Section 28).
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from research_agents.document_processing_agent.schemas import (
    DocumentChunk,
    DocumentProcessingOutput,
    EngineeringEntity,
    EngineeringFact,
    ExtractedReference,
    ExtractedSection,
)


class DocumentRepository(ABC):
    """Abstract persistence interface for processed documents, chunks, facts, and relationships."""

    @abstractmethod
    async def save_document(self, output: DocumentProcessingOutput) -> str:
        """Persists full document processing output."""
        pass

    @abstractmethod
    async def save_section(self, section: ExtractedSection, document_id: str) -> str:
        """Persists an extracted section."""
        pass

    @abstractmethod
    async def save_chunk(self, chunk: DocumentChunk) -> str:
        """Persists a single semantic document chunk."""
        pass

    @abstractmethod
    async def save_entity(self, entity: EngineeringEntity, document_id: str) -> str:
        """Persists an extracted engineering entity."""
        pass

    @abstractmethod
    async def save_fact(self, fact: EngineeringFact) -> str:
        """Persists an extracted engineering fact."""
        pass

    @abstractmethod
    async def save_reference(self, reference: ExtractedReference, document_id: str) -> str:
        """Persists an extracted bibliography reference."""
        pass

    @abstractmethod
    async def save_document_relationship(self, source_doc_id: str, target_doc_id: str, relationship: str) -> str:
        """Persists a relationship between two documents."""
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[DocumentProcessingOutput]:
        """Retrieves processed document by ID."""
        pass

    @abstractmethod
    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Retrieves all chunks belonging to a document."""
        pass

    @abstractmethod
    async def get_document_facts(self, document_id: str) -> List[EngineeringFact]:
        """Retrieves all facts derived from a document."""
        pass


class InMemoryDocumentRepository(DocumentRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._docs: Dict[str, DocumentProcessingOutput] = {}
        self._sections: Dict[str, List[ExtractedSection]] = {}
        self._chunks: Dict[str, List[DocumentChunk]] = {}
        self._entities: Dict[str, List[EngineeringEntity]] = {}
        self._facts: Dict[str, List[EngineeringFact]] = {}
        self._references: Dict[str, List[ExtractedReference]] = {}
        self._relationships: List[Tuple[str, str, str]] = []

    async def save_document(self, output: DocumentProcessingOutput) -> str:
        doc_id = output.document.document_id if output.document else (output.document_id or "unknown")
        self._docs[doc_id] = output
        self._chunks[doc_id] = output.chunks
        self._facts[doc_id] = output.facts
        self._sections[doc_id] = output.sections
        self._entities[doc_id] = output.entities
        self._references[doc_id] = output.references
        return doc_id

    async def save_section(self, section: ExtractedSection, document_id: str) -> str:
        if document_id not in self._sections:
            self._sections[document_id] = []
        self._sections[document_id].append(section)
        return f"{document_id}_sec_{len(self._sections[document_id])}"

    async def save_chunk(self, chunk: DocumentChunk) -> str:
        if chunk.document_id not in self._chunks:
            self._chunks[chunk.document_id] = []
        self._chunks[chunk.document_id].append(chunk)
        return chunk.chunk_id

    async def save_entity(self, entity: EngineeringEntity, document_id: str) -> str:
        if document_id not in self._entities:
            self._entities[document_id] = []
        self._entities[document_id].append(entity)
        return f"{document_id}_ent_{len(self._entities[document_id])}"

    async def save_fact(self, fact: EngineeringFact) -> str:
        doc_id = fact.source_document
        if doc_id not in self._facts:
            self._facts[doc_id] = []
        self._facts[doc_id].append(fact)
        return f"{doc_id}_fact_{len(self._facts[doc_id])}"

    async def save_reference(self, reference: ExtractedReference, document_id: str) -> str:
        if document_id not in self._references:
            self._references[document_id] = []
        self._references[document_id].append(reference)
        return reference.reference_id

    async def save_document_relationship(self, source_doc_id: str, target_doc_id: str, relationship: str) -> str:
        self._relationships.append((source_doc_id, target_doc_id, relationship))
        return f"{source_doc_id}->{relationship}->{target_doc_id}"

    async def get_document(self, document_id: str) -> Optional[DocumentProcessingOutput]:
        return self._docs.get(document_id)

    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        return self._chunks.get(document_id, [])

    async def get_document_facts(self, document_id: str) -> List[EngineeringFact]:
        return self._facts.get(document_id, [])


# Backward compatibility alias
ProcessedDocumentRepository = DocumentRepository
InMemoryProcessedDocumentRepository = InMemoryDocumentRepository
