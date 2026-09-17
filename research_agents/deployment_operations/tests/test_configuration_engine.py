"""Tests for configuration management and baselines."""
from research_agents.deployment_operations.schemas import ConfigurationItem, OperationalMode
from research_agents.deployment_operations.services.configuration_engine import ConfigurationEngine


def test_operational_baseline():
    engine = ConfigurationEngine()
    baseline = engine.create_operational_baseline("PROJ-1", "SYS-1")
    assert baseline.version == "1.0.0"
    assert baseline.is_active is True
    assert OperationalMode.NORMAL in baseline.approved_operating_modes
    assert len(baseline.configurations) >= 4
