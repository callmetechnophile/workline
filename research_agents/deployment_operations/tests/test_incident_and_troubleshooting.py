"""Tests for incident and troubleshooting engines."""
from research_agents.deployment_operations.schemas import AlertSeverity
from research_agents.deployment_operations.services.incident_engine import IncidentEngine
from research_agents.deployment_operations.services.troubleshooting_engine import TroubleshootingEngine


def test_log_incident():
    engine = IncidentEngine()
    inc = engine.log_incident("INC-01", "PROJ-1", "SYS-1", "Power drop", AlertSeverity.CRITICAL)
    assert inc.incident_id == "INC-01"
    assert inc.root_cause_type == "ROOT_CAUSE_HYPOTHESIS"


def test_troubleshooting_tree():
    engine = TroubleshootingEngine()
    tree = engine.build_troubleshooting_tree("SYS-1")
    assert len(tree.nodes) >= 2
    assert len(tree.nodes[0].possible_causes) >= 2
