"""
Observability, health metrics, and deterministic alerting engine.
"""

from typing import List
from research_agents.deployment_operations.schemas import (
    AlertRule,
    AlertSeverity,
    HealthMetric,
    SystemType,
)


class HealthObservabilityEngine:
    """Establishes operational telemetry, health checks, and alerting rules."""

    def configure_observability(
        self,
        system_id: str,
        system_type: SystemType,
    ) -> tuple[List[HealthMetric], List[AlertRule]]:
        metrics: List[HealthMetric] = []
        alerts: List[AlertRule] = []

        # 1. Health Metrics
        metrics.append(
            HealthMetric(
                metric_name="system_availability_ratio",
                current_value=0.9995,
                threshold_warning=0.9950,
                threshold_critical=0.9900,
                unit="ratio",
                status="HEALTHY",
            )
        )
        metrics.append(
            HealthMetric(
                metric_name="task_execution_latency_ms",
                current_value=45.0,
                threshold_warning=200.0,
                threshold_critical=500.0,
                unit="ms",
                status="HEALTHY",
            )
        )
        metrics.append(
            HealthMetric(
                metric_name="model_inference_error_rate",
                current_value=0.001,
                threshold_warning=0.02,
                threshold_critical=0.05,
                unit="ratio",
                status="HEALTHY",
            )
        )

        if system_type in [SystemType.PHYSICAL, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            metrics.append(
                HealthMetric(
                    metric_name="core_operating_temperature_c",
                    current_value=42.0,
                    threshold_warning=60.0,
                    threshold_critical=75.0,
                    unit="C",
                    status="HEALTHY",
                )
            )

        # 2. Alert Rules
        alerts.append(
            AlertRule(
                rule_id="ALERT-RULE-01",
                name="High Latency or Processing Backpressure",
                condition="task_execution_latency_ms > 200.0 for 3 consecutive intervals",
                severity=AlertSeverity.WARNING,
                affected_component="Control Fabric Task Dispatcher",
                response_procedure="Inspect worker queue depth; scale worker pool if CPU saturated.",
                escalation="Notify on-call SRE if latency exceeds 500ms.",
            )
        )
        alerts.append(
            AlertRule(
                rule_id="ALERT-RULE-02",
                name="Model Inference Outage or Quota Exhaustion",
                condition="model_inference_error_rate > 0.05",
                severity=AlertSeverity.CRITICAL,
                affected_component="Bedrock Reasoning Provider",
                response_procedure="Engage local deterministic heuristic fallback; verify AWS credentials.",
                escalation="Page Infrastructure Lead immediately.",
            )
        )
        if system_type in [SystemType.PHYSICAL, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            alerts.append(
                AlertRule(
                    rule_id="ALERT-RULE-03",
                    name="Chassis Over-Temperature",
                    condition="core_operating_temperature_c > 75.0",
                    severity=AlertSeverity.CRITICAL,
                    affected_component="Thermal Subsystem",
                    response_procedure="Throttle processing throughput; activate secondary fans.",
                    escalation="Initiate emergency shutdown if temp exceeds 85°C.",
                )
            )

        return metrics, alerts
