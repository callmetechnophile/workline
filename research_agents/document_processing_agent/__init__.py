"""
DocumentProcessingAgent — Agent #3 of WorkflowGuide AI Platform.
"""

from research_agents.document_processing_agent.agent import DocumentProcessingAgent
from research_agents.document_processing_agent.config import doc_config
from research_agents.document_processing_agent.schemas import (
    DocumentChunk,
    DocumentMetadata,
    DocumentProcessingInput,
    DocumentProcessingOutput,
    EngineeringEntity,
    EngineeringFact,
    ExtractedBlock,
    ExtractedFigure,
    ExtractedLink,
    ExtractedReference,
    ExtractedSection,
    ExtractedTable,
    StructuredError,
)

__all__ = [
    "DocumentProcessingAgent",
    "DocumentProcessingInput",
    "DocumentProcessingOutput",
    "DocumentMetadata",
    "ExtractedBlock",
    "ExtractedSection",
    "ExtractedTable",
    "ExtractedFigure",
    "ExtractedLink",
    "ExtractedReference",
    "DocumentChunk",
    "EngineeringEntity",
    "EngineeringFact",
    "StructuredError",
    "doc_config",
]
