"""Tests for Change Security Impact and Security Regression Detection."""
from research_agents.security_threat.schemas import SecurityControl, ThreatObject
from research_agents.security_threat.services.change_security_engine import ChangeSecurityEngine

def test_change_security_regression():
    engine = ChangeSecurityEngine()
    chg = {
        "change_id": "CHG-001",
        "project_id": "P1",
        "description": "Disable auth middleware for debugging public endpoint",
        "target_artifact": "API",
    }
    threats = [ThreatObject(threat_id="T1", project_id="P1", title="Auth Bypass")]
    controls = [SecurityControl(control_id="C1", name="Auth", category="AUTHENTICATION")]
    impact = engine.evaluate_change_security_impact(chg, threats, controls)
    assert impact.is_regression is True
    assert len(impact.new_attack_surfaces) == 1
