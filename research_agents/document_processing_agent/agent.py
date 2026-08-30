"""
Agent #3: DocumentProcessingAgent implementation using Google ADK conventions.
Converts raw PDFs, HTML, and text documents into normalized Markdown, semantic chunks,
code snippets, and verifiable engineering facts with strict character/page provenance.
"""

import asyncio
import hashlib
import time
from typing import Dict, List, Optional, Tuple
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
    DocumentChunk,
    DocumentMetadata,
    DocumentProcessingInput,
    DocumentProcessingOutput,
    DocumentSummary,
    EngineeringEntity,
    EngineeringFact,
    ExtractedBlock,
    ExtractedCodeBlock,
    ExtractedFigure,
    ExtractedLink,
    ExtractedReference,
    ExtractedSection,
    ExtractedTable,
    StructuredError,
)
from research_agents.document_processing_agent.services.chunker import SemanticChunker
from research_agents.document_processing_agent.services.code_extractor import CodeBlockExtractor
from research_agents.document_processing_agent.services.entity_extractor import EngineeringEntityExtractor
from research_agents.document_processing_agent.services.fact_extractor import EngineeringFactExtractor
from research_agents.document_processing_agent.services.file_exporter import DocumentFileExporter
from research_agents.document_processing_agent.services.markdown_builder import MarkdownBuilder
from research_agents.document_processing_agent.services.quality_evaluator import QualityEvaluator
from research_agents.document_processing_agent.services.validator import DocumentValidator


class DocumentProcessingAgent:
    """
    Google ADK-compliant Document Processing & Evidence Extraction Agent (Agent #3).
    Converts technical documents into structured, provenance-preserving engineering evidence.
    """

    NAME = "DocumentProcessingAgent"
    DESCRIPTION = (
        "Converts technical documents into structured, provenance-preserving engineering evidence."
    )
    CAPABILITIES = [
        "document.process",
        "document.extract",
        "document.chunk",
        "document.entities",
        "document.facts",
        "document.metadata",
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
        code_extractor: Optional[CodeBlockExtractor] = None,
        file_exporter: Optional[DocumentFileExporter] = None,
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
        self.code_extractor = code_extractor or CodeBlockExtractor()
        self.file_exporter = file_exporter or DocumentFileExporter()
        self.quality_evaluator = quality_evaluator or QualityEvaluator()

    async def run(
        self,
        input_data: DocumentProcessingInput,
        execution_id: Optional[str] = None,
    ) -> DocumentProcessingOutput:
        """
        Executes the full document ingestion, parsing, chunking, and fact extraction pipeline.
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
            document_hash = hashlib.sha256(content_bytes).hexdigest()
        except ParserError as pe:
            logger.error(f"[{exec_id}][{self.NAME}] Validation/Fetch error: {pe.message}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                document=DocumentSummary(
                    document_id=input_data.document_id,
                    title=input_data.title,
                    source_url=input_data.source_url,
                    quality_score=0.0,
                ),
                metadata=DocumentMetadata(title=input_data.title, url=input_data.source_url),
                quality_score=0.0,
                warnings=[pe.message],
                errors=[StructuredError(code=pe.code, message=pe.message, retryable=pe.retryable)],
            )
        except Exception as e:
            logger.error(f"[{exec_id}][{self.NAME}] Unexpected fetch error: {str(e)}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                document=DocumentSummary(
                    document_id=input_data.document_id,
                    title=input_data.title,
                    source_url=input_data.source_url,
                    quality_score=0.0,
                ),
                metadata=DocumentMetadata(title=input_data.title, url=input_data.source_url),
                quality_score=0.0,
                warnings=[str(e)],
                errors=[StructuredError(code="INTERNAL_FETCH_ERROR", message=str(e), retryable=False)],
            )

        # 2. Select Parser
        parser = self._select_parser(doc_type)

        # 3. Parse Document
        try:
            metadata, blocks, tables, figures, links, references = parser.parse(
                content_bytes=content_bytes,
                source_url=input_data.source_url,
                title_hint=input_data.title,
            )
            metadata.document_hash = document_hash
        except CorruptedDocumentError as cde:
            logger.error(f"[{exec_id}][{self.NAME}] Corrupted document: {cde.message}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                document=DocumentSummary(
                    document_id=input_data.document_id,
                    title=input_data.title,
                    document_type=doc_type,
                    document_hash=document_hash,
                    quality_score=0.0,
                ),
                metadata=DocumentMetadata(title=input_data.title, document_type=doc_type, document_hash=document_hash),
                quality_score=0.0,
                warnings=[cde.message],
                errors=[StructuredError(code=cde.code, message=cde.message, retryable=False)],
            )
        except Exception as pe:
            logger.error(f"[{exec_id}][{self.NAME}] Parser failure: {str(pe)}")
            return DocumentProcessingOutput(
                status="error",
                document_id=input_data.document_id,
                document=DocumentSummary(
                    document_id=input_data.document_id,
                    title=input_data.title,
                    document_type=doc_type,
                    document_hash=document_hash,
                    quality_score=0.0,
                ),
                metadata=DocumentMetadata(title=input_data.title, document_type=doc_type, document_hash=document_hash),
                quality_score=0.0,
                warnings=[str(pe)],
                errors=[StructuredError(code="PARSE_FAILURE", message=str(pe), retryable=False)],
            )

        # 4. Normalized Markdown Generation
        markdown_str, sections = self.generate_markdown(metadata, blocks, tables)

        # 5. Semantic Chunking
        chunks = self.chunk_document(input_data.document_id, sections, input_data.source_url)

        # 6. Extract Code Blocks
        code_blocks = self.extract_code(blocks)

        # 7. Extract Engineering Entities
        entities = self.extract_entities(blocks)

        # 8. Extract Engineering Facts
        facts = self.extract_facts(input_data.document_id, blocks)

        # 9. Quality Evaluation & OCR Check
        status, quality_score, quality_warnings = self.quality_evaluator.evaluate(
            metadata=metadata,
            blocks=blocks,
            sections=sections,
            tables=tables,
        )

        elapsed = time.time() - start_time

        summary = DocumentSummary(
            document_id=input_data.document_id,
            title=metadata.title,
            document_type=metadata.document_type,
            source_url=input_data.source_url,
            page_count=metadata.page_count,
            quality_score=quality_score,
            document_hash=document_hash,
        )

        output = DocumentProcessingOutput(
            status=status,
            document=summary,
            document_id=input_data.document_id,
            metadata=metadata,
            markdown=markdown_str,
            sections=sections,
            chunks=chunks,
            entities=entities,
            facts=facts,
            tables=tables,
            figures=figures,
            code_blocks=code_blocks,
            references=references,
            links=links,
            warnings=quality_warnings,
            errors=errors,
            quality_score=quality_score,
        )

        # 10. Local File Export (Section 23)
        if input_data.output_dir:
            try:
                self.file_exporter.export(output, input_data.output_dir, overwrite=True)
                logger.info(f"[{exec_id}][{self.NAME}] Exported artifacts to '{input_data.output_dir}'")
            except Exception as exp_err:
                logger.error(f"[{exec_id}][{self.NAME}] Export failed: {exp_err}")
                output.warnings.append(f"Export warning: {str(exp_err)}")

        # Observability Log (Section 38)
        logger.info(
            f"[{exec_id}][{self.NAME}] Processing finished: agent_id='{self.NAME}' "
            f"document_id='{input_data.document_id}' document_hash='{document_hash[:12]}' "
            f"processing_time={elapsed:.3f}s page_count={metadata.page_count} chunk_count={len(chunks)} "
            f"warning_count={len(quality_warnings)} error_count={len(errors)}"
        )

        return output

    def run_sync(
        self,
        input_data: DocumentProcessingInput,
        execution_id: Optional[str] = None,
    ) -> DocumentProcessingOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods (Section 24)
    # =========================================================================

    def process_document(self, input_data: DocumentProcessingInput) -> DocumentProcessingOutput:
        """ADK Capability: Synchronously processes a document."""
        return self.run_sync(input_data)

    def extract_text(self, blocks: List[ExtractedBlock]) -> str:
        """ADK Capability: Combines block texts into clean normalized document text."""
        return "\n\n".join(b.text for b in blocks if b.text.strip())

    def extract_metadata(self, content_bytes: bytes, doc_type: str = "pdf") -> DocumentMetadata:
        """ADK Capability: Extracts document metadata."""
        parser = self._select_parser(doc_type)
        meta, _, _, _, _, _ = parser.parse(content_bytes)
        return meta

    def extract_sections(self, blocks: List[ExtractedBlock], tables: List[ExtractedTable]) -> List[ExtractedSection]:
        """ADK Capability: Groups blocks into structured sections."""
        _, sections = self.markdown_builder.build_markdown(DocumentMetadata(), blocks, tables)
        return sections

    def extract_tables(self, content_bytes: bytes, doc_type: str = "pdf") -> List[ExtractedTable]:
        """ADK Capability: Extracts structured tables from document bytes."""
        parser = self._select_parser(doc_type)
        _, _, tables, _, _, _ = parser.parse(content_bytes)
        return tables

    def extract_entities(self, blocks: List[ExtractedBlock]) -> List[EngineeringEntity]:
        """ADK Capability: Identifies engineering hardware and software entities."""
        return self.entity_extractor.extract_entities(blocks)

    def extract_facts(self, document_id: str, blocks: List[ExtractedBlock]) -> List[EngineeringFact]:
        """ADK Capability: Extracts verifiable factual statements."""
        return self.fact_extractor.extract_facts(document_id, blocks)

    def extract_code(self, blocks: List[ExtractedBlock]) -> List[ExtractedCodeBlock]:
        """ADK Capability: Identifies and extracts code snippets."""
        return self.code_extractor.extract_code_blocks(blocks)

    def chunk_document(
        self,
        document_id: str,
        sections: List[ExtractedSection],
        source_url: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """ADK Capability: Creates semantic document chunks."""
        return self.chunker.chunk_document(document_id, sections, source_url)

    def generate_markdown(
        self,
        metadata: DocumentMetadata,
        blocks: List[ExtractedBlock],
        tables: List[ExtractedTable],
    ) -> Tuple[str, List[ExtractedSection]]:
        """ADK Capability: Generates normalized Markdown with provenance."""
        return self.markdown_builder.build_markdown(metadata, blocks, tables)

    def _select_parser(self, doc_type: str) -> BaseDocumentParser:
        if doc_type == "pdf":
            return self.pdf_parser
        elif doc_type == "html":
            return self.html_parser
        return self.text_parser
