"""
Unified Retrieval & Evidence subsystem.
"""

from backend.workline.retrieval_service.models import Evidence, RetrievalQuery, RetrievalResult
from backend.workline.retrieval_service.service import (
    UnifiedRetrievalService,
    default_retrieval_service,
)

__all__ = [
    "Evidence",
    "RetrievalQuery",
    "RetrievalResult",
    "UnifiedRetrievalService",
    "default_retrieval_service",
]
