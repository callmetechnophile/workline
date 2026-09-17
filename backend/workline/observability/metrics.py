"""
Lightweight in-memory Prometheus-compatible metrics collector.
"""

from collections import defaultdict
import threading
from typing import Dict, Any


class MetricsCollector:
    """Thread-safe Prometheus-compatible metrics counter and summary collector."""

    def __init__(self):
        self._lock = threading.Lock()
        self._request_counts: Dict[str, int] = defaultdict(int)
        self._job_counts: Dict[str, int] = defaultdict(int)
        self._errors: int = 0
        self._total_duration: float = 0.0

    def record_request(self, method: str, path: str, status_code: int, duration_s: float):
        key = f"{method}_{status_code}"
        with self._lock:
            self._request_counts[key] += 1
            self._total_duration += duration_s
            if status_code >= 400:
                self._errors += 1

    def record_job_status(self, job_type: str, status: str):
        key = f"{job_type}_{status}"
        with self._lock:
            self._job_counts[key] += 1

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "request_counts": dict(self._request_counts),
                "job_counts": dict(self._job_counts),
                "total_errors": self._errors,
                "total_duration_seconds": round(self._total_duration, 3),
            }


default_metrics_collector = MetricsCollector()
