"""Tests for Security Test Specification Generator."""
from research_agents.security_threat.schemas import ThreatObject
from research_agents.security_threat.services.security_test_generator import SecurityTestGenerator

def test_generate_security_tests():
    gen = SecurityTestGenerator()
    threats = [
        ThreatObject(threat_id="T-PI", project_id="P1", title="PI", category="PROMPT_INJECTION"),
        ThreatObject(threat_id="T-TENANT", project_id="P1", title="Tenant", category="TENANT_ISOLATION"),
        ThreatObject(threat_id="T-A2A", project_id="P1", title="A2A", category="A2A_ATTACK"),
    ]
    tests = gen.generate_tests_for_threats(threats)
    assert len(tests) == 3
    types = [t.test_type for t in tests]
    assert "PROMPT_INJECTION" in types
    assert "TENANT_ISOLATION" in types
    assert "A2A_SECURITY" in types
