"""Tests for WBSEngine."""
from research_agents.project_execution_agent.services.wbs_engine import WBSEngine

def test_wbs_partitioning():
    engine = WBSEngine()
    arch = {"subsystems": ["ThermalImaging", "FlightController", "PowerManagement"]}
    packages = engine.partition_architecture(arch, {}, {})
    assert len(packages) >= 3
    wp_titles = [wp.title for wp in packages]
    assert "System Core & Environment Setup" in wp_titles
    assert "Subsystems & Core Modules" in wp_titles
    assert "Automated Quality Gates & Test Suite" in wp_titles
