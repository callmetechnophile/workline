"""Tests for STRIDE, Agentic Threat Modeling, and Deterministic Scoring."""
from research_agents.security_threat.schemas import ThreatObject
from research_agents.security_threat.services.threat_modeling_engine import ThreatModelingEngine

def test_deterministic_risk_scoring():
    engine = ThreatModelingEngine()
    score = engine.calculate_risk_score(likelihood=4, impact=5)
    assert score == 20

def test_critical_threat_override():
    engine = ThreatModelingEngine()
    t_crit = ThreatObject(
        threat_id="T-CRIT",
        project_id="P1",
        title="RCE in Shell Tool",
        category="REMOTE_EXECUTION",
        severity=5,
        likelihood=4,
        risk_score=20,
    )
    assert engine.is_critical_threat(t_crit) is True

def test_attack_path_building():
    engine = ThreatModelingEngine()
    t = ThreatObject(
        threat_id="THREAT-PI-01",
        project_id="P1",
        title="Prompt Injection",
        category="PROMPT_INJECTION",
    )
    paths = engine.build_attack_paths([t], [])
    assert len(paths) == 1
    assert "ASSET-AGENT-RUN" in paths[0].target_asset
