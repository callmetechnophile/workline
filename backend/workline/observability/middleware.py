"""
Correlation ID & Request Tracing Middleware.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger

from backend.workline.observability.metrics import default_metrics_collector


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Injects X-Correlation-ID header, logs request latency, and increments metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:
        corr_id = request.headers.get("X-Correlation-ID") or f"corr_{uuid.uuid4().hex[:12]}"
        start_time = time.time()

        # Contextual log
        logger.debug(f"[HTTP] [{corr_id}] -> {request.method} {request.url.path}")

        response = await call_next(request)

        duration = time.time() - start_time
        response.headers["X-Correlation-ID"] = corr_id
        response.headers["X-Process-Time"] = f"{duration:.4f}"

        # Record metrics
        default_metrics_collector.record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_s=duration,
        )

        logger.debug(f"[HTTP] [{corr_id}] <- {response.status_code} ({duration*1000:.1f}ms)")
        return response
