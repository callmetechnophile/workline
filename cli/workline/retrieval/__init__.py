"""
Retrieval package for WORKLINE CLI and Local Moss integration.
"""

from cli.workline.retrieval.record import EngineeringRecord
from cli.workline.retrieval.parsers import parse_file_into_records, infer_resource_type
from cli.workline.retrieval.local_engine import LocalRetrievalEngine
from cli.workline.retrieval.moss_adapter import LocalMossAdapter
from cli.workline.retrieval.indexer import ProjectIndexer, IndexingStats
from cli.workline.retrieval.retriever import ProjectRetriever
from cli.workline.retrieval.context import ContextBuilder, ContextBundle

__all__ = [
    "EngineeringRecord",
    "parse_file_into_records",
    "infer_resource_type",
    "LocalRetrievalEngine",
    "LocalMossAdapter",
    "ProjectIndexer",
    "IndexingStats",
    "ProjectRetriever",
    "ContextBuilder",
    "ContextBundle",
]
