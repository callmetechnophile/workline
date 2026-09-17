"""Tests for environment validation."""
from research_agents.deployment_operations.schemas import SystemType
from research_agents.deployment_operations.services.environment_validator import EnvironmentValidator


def test_environment_validator_physical():
    validator = EnvironmentValidator()
    install_reqs, env_reqs = validator.inspect_requirements(SystemType.PHYSICAL)
    assert len(install_reqs) >= 3
    cats = [r.category for r in install_reqs]
    assert "POWER" in cats
    assert "COOLING" in cats


def test_environment_validator_software():
    validator = EnvironmentValidator()
    install_reqs, env_reqs = validator.inspect_requirements(SystemType.SOFTWARE)
    assert len(env_reqs) >= 3
    resources = [r.resource for r in env_reqs]
    assert "SURREALDB_CONNECTIVITY" in resources
