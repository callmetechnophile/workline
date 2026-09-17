"""
Observability and Operational Metrics Endpoints.
"""

from fastapi import APIRouter
from backend.workline.observability.metrics import default_metrics_collector

router = APIRouter(prefix="/api/observability", tags=["Observability"])


@router.get("/metrics")
async def get_metrics():
    """Retrieve platform runtime metrics and request counts."""
    return default_metrics_collector.get_summary()
