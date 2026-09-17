"""Tests for health and observability engine."""
from research_agents.deployment_operations.schemas import AlertSeverity, SystemType
from research_agents.deployment_operations.services.health_observability_engine import HealthObservabilityEngine


def test_configure_observability():
    engine = HealthObservabilityEngine()
    metrics, alerts = engine.configure_observability("SYS-1", SystemType.HYBRID)
    assert len(metrics) >= 3
    metric_names = [m.metric_name for m in metrics]
    assert "system_availability_ratio" in metric_names
    assert "task_execution_latency_ms" in metric_names

    assert len(alerts) >= 2
    severities = [a.severity for a in alerts]
    assert AlertSeverity.CRITICAL in severities
