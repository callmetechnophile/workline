"""
Agent #3: DocumentProcessingAgent implementation using Google ADK conventions.
Converts raw PDFs, HTML, and text documents into normalized Markdown, semantic chunks,
and verifiable engineering facts with strict character/page provenance.
"""

import asyncio
import time
from typing import Dict, List, Optional
import uuid
from loguru import logger

from research_agents.document_processing_agent.parsers.base import (
    BaseDocumentParser,
    CorruptedDocumentError,
    ParserError,
    UnsupportedFormatError,
)
from research_agents.document_processing_agent.parsers.html_parser import HTMLDocumentParser
from research_agents.document_processing_agent.parsers.pdf_parser import PDFDocumentParser
from research_agents.document_processing_agent.parsers.text_parser import TextDocumentParser
from research_agents.document_processing_agent.schemas import (
    DocumentMetadata,
    DocumentProcessingInput,
    DocumentProcessingOutput,
    StructuredError,
)
from research_agents.document_processing_agent.services.chunker import SemanticChunker
from research_agents.document_processing_agent.services.entity_extractor import EngineeringEntityExtractor
from research_agents.document_processing_agent.services.fact_extractor import EngineeringFactExtractor
from research_agents.document_processing_agent.services.markdown_builder import MarkdownBuilder
from research_agents.document_processing_agent.services.quality_evaluator import QualityEvaluator
from research_agents.document_processing_agent.services.validator import DocumentValidator


class DocumentProcessingAgent:
    """
    Google ADK-compliant Document Processing & Evidence Extraction Agent.
    Preprocesses technical documents, datasheets, and research papers into structured Markdown and evidence.
    """

    NAME = "DocumentProcessingAgent"
    DESCRIPTION = (
        "Converts research papers, datasheets, and technical web documents into "
        "structured Markdown, semantic chunks, and verified engineering facts."
    )
    CAPABILITIES = [
        "document.process",
        "document.chunk",
        "document.extract_facts",
        "document.markdown",
    ]

    def __init__(
        self,
        validator: Optional[DocumentValidator] = None,
        pdf_parser: Optional[BaseDocumentParser] = None,
        html_parser: Optional[BaseDocumentParser] = None,
        text_parser: Optional[BaseDocumentParser] = None,
        markdown_builder: Optional[MarkdownBuilder] = None,
        chunker: Optional[SemanticChunker] = None,
        entity_extractor: Optional[EngineeringEntityExtractor] = None,
        fact_extractor: Optional[EngineeringFactExtractor] = None,
        quality_evaluator: Optional[QualityEvaluator] = None,
    ):
        self.validator = validator or DocumentValidator()
        self.pdf_parser = pdf_parser or PDFDocumentParser()
        self.html_parser = html_parser or HTMLDocumentParser()
        self.text_parser = text_parser or TextDocumentParser()
        self.markdown_builder = markdown_builder or MarkdownBuilder()
        self.chunker = chunker or SemanticChunker()
        self.entity_extractor = entity_extractor or EngineeringEntityExtractor()
        self.fact_extractor = fact_extractor or EngineeringFactExtractor()
        self.quality_evaluator = quality_evaluator or QualityEvaluator()

    async def run(
        self,
        input_data: DocumentProcessingInput,
        execution_id: Optional[str] = None,
    ) -> DocumentProcessingOutput:
        """
        Executes the document ingestion, parsing, chunking, and fact extraction pipeline.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.request_context.execution_id if input_data.request_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        logger.info(
            f"[{exec_id}][{self.NAME}] Processing document_id='{input_data.document_id}' "
            f"type='{input_data.document_type}' source='{input_data.source_url or input_data.local_path}'"
        )

        errors: List[StructuredError] = []

        # 1. Fetch & Validate Document Bytes
        try:
            content_bytes, doc_type = await self.validator.fetch_document(input_data)
        except ParserError as pe:
            logger.error(f"[{exec_id}][{self.NAME}] Validation/Fetch error: {pe.message}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                metadata=DocumentMetadata(title=input_data.title, url=input_data.source_url),
                quality_score=0.0,
                quality_warnings=[pe.message],
                errors=[StructuredError(code=pe.code, message=pe.message, retryable=pe.retryable)],
            )
        except Exception as e:
            logger.error(f"[{exec_id}][{self.NAME}] Unexpected fetch error: {str(e)}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                metadata=DocumentMetadata(title=input_data.title, url=input_data.source_url),
                quality_score=0.0,
                quality_warnings=[str(e)],
                errors=[StructuredError(code="INTERNAL_FETCH_ERROR", message=str(e), retryable=False)],
            )

        # 2. Select Appropriate Parser
        if doc_type == "pdf":
            parser = self.pdf_parser
        elif doc_type == "html":
            parser = self.html_parser
        else:
            parser = self.text_parser

        # 3. Parse Document
        try:
            metadata, blocks, tables, figures, links, references = parser.parse(
                content_bytes=content_bytes,
                source_url=input_data.source_url,
                title_hint=input_data.title,
            )
        except CorruptedDocumentError as cde:
            logger.error(f"[{exec_id}][{self.NAME}] Corrupted document: {cde.message}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                metadata=DocumentMetadata(title=input_data.title, document_type=doc_type),
                quality_score=0.0,
                quality_warnings=[cde.message],
                errors=[StructuredError(code=cde.code, message=cde.message, retryable=False)],
            )
        except Exception as pe:
            logger.error(f"[{exec_id}][{self.NAME}] Parser failure: {str(pe)}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                metadata=DocumentMetadata(title=input_data.title, document_type=doc_type),
                quality_score=0.0,
                quality_warnings=[str(pe)],
                errors=[StructuredError(code="PARSE_FAILURE", message=str(pe), retryable=False)],
            )

        # 4. Synthesize Normalized Markdown with Page Provenance
        markdown_str, sections = self.markdown_builder.build_markdown(
            metadata=metadata,
            blocks=blocks,
            tables=tables,
        )

        # 5. Semantic Chunking
        chunks = self.chunker.chunk_document(
            document_id=input_data.document_id,
            sections=sections,
            source_url=input_data.source_url,
        )

        # 6. Extract Engineering Entities
        entities = self.entity_extractor.extract_entities(blocks)

        # 7. Extract Engineering Facts with Strict Provenance
        facts = self.fact_extractor.extract_facts(
            document_id=input_data.document_id,
            blocks=blocks,
        )

        # 8. Evaluate Processing Quality & OCR Requirement
        status, quality_score, quality_warnings = self.quality_evaluator.evaluate(
            metadata=metadata,
            blocks=blocks,
            sections=sections,
            tables=tables,
        )

        elapsed = time.time() - start_time
        logger.info(
            f"[{exec_id}][{self.NAME}] Completed processing in {elapsed:.3f}s. "
            f"Status: '{status}', Pages: {metadata.page_count}, Chunks: {len(chunks)}, "
            f"Entities: {len(entities)}, Facts: {len(facts)}, Quality: {quality_score}"
        )

        return DocumentProcessingOutput(
            status=status,
            document_id=input_data.document_id,
            metadata=metadata,
            markdown=markdown_str,
            sections=sections,
            tables=tables,
            figures=figures,
            links=links,
            references=references,
            chunks=chunks,
            entities=entities,
            facts=facts,
            quality_score=quality_score,
            quality_warnings=quality_warnings,
            errors=errors,
        )

    def run_sync(
        self,
        input_data: DocumentProcessingInput,
        execution_id: Optional[str] = None,
    ) -> DocumentProcessingOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))
