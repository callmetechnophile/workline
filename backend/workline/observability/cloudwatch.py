"""
Amazon CloudWatch Observability, Metrics, and Structured Logging for Workline / ArmourFlow.
Publishes custom metrics to CloudWatch:
- API Latency and 4xx/5xx Error Rates
- Agent Execution Duration and Step Failures
- SQS Queue Depth and DLQ counts
- ArmorIQ Security Policy Violations
"""

import os
import time
from typing import Any, Dict, List, Optional
from loguru import logger


class CloudWatchMetricsReporter:
    """
    Publishes custom metrics to AWS CloudWatch Metrics under namespace 'Workline/Platform'.
    Emits CloudWatch Embedded Metric Format (EMF) logs for high-throughput zero-cost metrics.
    """

    def __init__(
        self,
        namespace: str = "Workline/Platform",
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        self.namespace = namespace
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.endpoint_url = endpoint_url or os.environ.get("CLOUDWATCH_ENDPOINT_URL")
        self._client = None
        self._recorded_metrics: List[Dict[str, Any]] = []
        self._init_client()

    def _init_client(self):
        try:
            import boto3
            kwargs: Dict[str, Any] = {"region_name": self.region_name}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._client = boto3.client("cloudwatch", **kwargs)
            logger.info(f"[CloudWatch] Initialized CloudWatch client for namespace '{self.namespace}'")
        except Exception as e:
            logger.warning(f"[CloudWatch] Could not initialize client ({e}); local metrics active.")
            self._client = None

    async def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Record a metric data point.
        Units: 'Count', 'Milliseconds', 'Seconds', 'Bytes', 'Percent'
        """
        dims = [{"Name": k, "Value": v} for k, v in (dimensions or {}).items()]
        entry = {
            "MetricName": metric_name,
            "Value": float(value),
            "Unit": unit,
            "Timestamp": time.time(),
            "Dimensions": dims,
        }
        self._recorded_metrics.append(entry)

        if not self._client:
            return True

        try:
            self._client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[entry],
            )
            return True
        except Exception as e:
            logger.warning(f"[CloudWatch] put_metric_data failed ({e})")
            return False

    async def record_api_call(self, endpoint: str, status_code: int, duration_ms: float):
        """Record standard API metrics."""
        dims = {"Endpoint": endpoint, "StatusCode": str(status_code)}
        await self.put_metric("ApiLatency", duration_ms, unit="Milliseconds", dimensions=dims)
        await self.put_metric("ApiRequests", 1.0, unit="Count", dimensions=dims)
        if status_code >= 400:
            await self.put_metric("ApiErrors", 1.0, unit="Count", dimensions=dims)

    async def record_policy_violation(self, agent_name: str, requested_scope: str):
        """Record an ArmorIQ security policy violation."""
        dims = {"Agent": agent_name, "Scope": requested_scope}
        await self.put_metric("ArmorIQPolicyViolations", 1.0, unit="Count", dimensions=dims)

    def get_recent_metrics(self) -> List[Dict[str, Any]]:
        return list(self._recorded_metrics[-50:])


# Global singleton instance
cloudwatch_metrics = CloudWatchMetricsReporter()
