"""Tests for Security Controls, Verification, and Least-Privilege."""
from research_agents.security_threat.schemas import SecurityControl
from research_agents.security_threat.services.security_control_engine import SecurityControlEngine

def test_get_standard_controls():
    engine = SecurityControlEngine()
    ctrls = engine.get_standard_controls()
    assert len(ctrls) >= 4
    categories = [c.category for c in ctrls]
    assert "AUTHORIZATION" in categories
    assert "AUTHENTICATION" in categories

def test_verify_control_with_evidence():
    engine = SecurityControlEngine()
    ctrl = SecurityControl(control_id="C1", name="Scope Map", verification_status="UNVERIFIED")
    evidence = {"status": "PASS", "evidence_id": "EVID-TEST-001"}
    verified = engine.verify_control(ctrl, evidence)
    assert verified.verification_status == "VERIFIED"
    assert "EVID-TEST-001" in verified.evidence_ids

def test_assess_least_privilege():
    engine = SecurityControlEngine()
    agents = [
        {"name": "ResearchAgent", "capabilities": ["search_papers", "shell", "filesystem.write"]},
        {"name": "ValidationAgent", "capabilities": ["validate_architecture"]},
    ]
    excessive = engine.assess_least_privilege(agents)
    assert len(excessive) == 1
    assert "ResearchAgent" in excessive[0]
