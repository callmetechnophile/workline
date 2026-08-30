"""
Root alias module proxying to research_agents.document_processing_agent.
Allows direct execution via `python -m document_processing_agent`.
"""

from research_agents.document_processing_agent import (
    DocumentChunk,
    DocumentMetadata,
    DocumentProcessingAgent,
    DocumentProcessingInput,
    DocumentProcessingOutput,
    EngineeringEntity,
    EngineeringFact,
    doc_config,
)

__all__ = [
    "DocumentProcessingAgent",
    "DocumentProcessingInput",
    "DocumentProcessingOutput",
    "DocumentMetadata",
    "DocumentChunk",
    "EngineeringEntity",
    "EngineeringFact",
    "doc_config",
]
