"""Tests for dependency engine."""
from research_agents.deployment_operations.schemas import SystemType
from research_agents.deployment_operations.services.dependency_engine import DependencyEngine


def test_dependency_analysis():
    engine = DependencyEngine()
    deps = engine.analyze_dependencies("SYS-1", SystemType.HYBRID)
    dep_targets = [d.target_service_or_component for d in deps]
    assert "SurrealDB Graph Database" in dep_targets
    assert "Amazon Bedrock Inference" in dep_targets
    assert "Unified Agent Control Fabric" in dep_targets
    spof_deps = [d for d in deps if d.is_single_point_of_failure]
    assert len(spof_deps) >= 1
