"""Tests for Agent #26 schemas."""
from research_agents.deployment_operations.schemas import (
    AlertSeverity,
    CommissioningStatus,
    DeploymentStage,
    IncidentState,
    MaintenanceType,
    OperationalMode,
    ReadinessStatus,
    ServiceabilityRating,
    SystemType,
)


def test_enums():
    assert SystemType.PHYSICAL == "PHYSICAL"
    assert SystemType.AI_AGENT == "AI_AGENT"
    assert DeploymentStage.OPERATIONAL == "OPERATIONAL"
    assert ReadinessStatus.BLOCKED == "BLOCKED"
    assert CommissioningStatus.PASS == "PASS"
    assert AlertSeverity.CRITICAL == "CRITICAL"
    assert IncidentState.DETECTED == "DETECTED"
    assert ServiceabilityRating.SERVICEABILITY_ACCEPTABLE == "SERVICEABILITY_ACCEPTABLE"
    assert MaintenanceType.PREVENTIVE == "PREVENTIVE"
    assert OperationalMode.NORMAL == "NORMAL"
