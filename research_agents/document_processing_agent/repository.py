"""
Repository interface for processed document, markdown, chunk, and fact storage.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.document_processing_agent.schemas import (
    DocumentChunk,
    DocumentProcessingOutput,
    EngineeringFact,
)


class ProcessedDocumentRepository(ABC):
    """Abstract persistence interface for processed documents, chunks, and facts."""

    @abstractmethod
    async def save_processed_document(self, output: DocumentProcessingOutput) -> str:
        """Persists full document processing output."""
        pass

    @abstractmethod
    async def save_chunk(self, chunk: DocumentChunk) -> str:
        """Persists a single semantic document chunk."""
        pass

    @abstractmethod
    async def save_fact(self, fact: EngineeringFact) -> str:
        """Persists an extracted engineering fact."""
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


class InMemoryProcessedDocumentRepository(ProcessedDocumentRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._docs: Dict[str, DocumentProcessingOutput] = {}
        self._chunks: Dict[str, List[DocumentChunk]] = {}
        self._facts: Dict[str, List[EngineeringFact]] = {}

    async def save_processed_document(self, output: DocumentProcessingOutput) -> str:
        self._docs[output.document_id] = output
        self._chunks[output.document_id] = output.chunks
        self._facts[output.document_id] = output.facts
        return output.document_id

    async def save_chunk(self, chunk: DocumentChunk) -> str:
        if chunk.document_id not in self._chunks:
            self._chunks[chunk.document_id] = []
        self._chunks[chunk.document_id].append(chunk)
        return chunk.chunk_id

    async def save_fact(self, fact: EngineeringFact) -> str:
        doc_id = fact.source_document
        if doc_id not in self._facts:
            self._facts[doc_id] = []
        self._facts[doc_id].append(fact)
        return f"{doc_id}_fact_{len(self._facts[doc_id])}"

    async def get_document(self, document_id: str) -> Optional[DocumentProcessingOutput]:
        return self._docs.get(document_id)

    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        return self._chunks.get(document_id, [])

    async def get_document_facts(self, document_id: str) -> List[EngineeringFact]:
        return self._facts.get(document_id, [])
