"""FastAPI administrative and observability endpoints for KnowledgeCache."""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from backend.workline.knowledge.cache.cache import knowledge_cache

router = APIRouter(prefix="/api/cache", tags=["Cache"])


@router.get("/stats")
def get_cache_stats() -> Dict[str, Any]:
    """Retrieve L1/L2 cache hit rate, entries, and memory metrics."""
    return knowledge_cache.get_stats().model_dump()


@router.get("/status")
def get_cache_status() -> Dict[str, Any]:
    """Check cache operational status and storage health."""
    stats = knowledge_cache.get_stats()
    return {
        "status": "HEALTHY",
        "l1_memory": f"{stats.l1_entries} entries",
        "l2_persistent": f"{stats.l2_entries} entries ({stats.l2_size_bytes} bytes)",
        "hit_rate": f"{stats.hit_rate:.1f}%",
        "miss_rate": f"{stats.miss_rate:.1f}%",
    }


@router.post("/clean")
def clean_expired_cache() -> Dict[str, Any]:
    """Remove expired TTL cache entries from memory and disk."""
    expired_count = knowledge_cache.clear_expired()
    return {
        "status": "COMPLETED",
        "expired_entries_cleared": expired_count,
    }


@router.post("/clear")
def clear_all_cache() -> Dict[str, Any]:
    """Flush all non-authoritative L1 and L2 cache items."""
    knowledge_cache.clear()
    return {
        "status": "COMPLETED",
        "message": "Knowledge cache flushed successfully",
    }
