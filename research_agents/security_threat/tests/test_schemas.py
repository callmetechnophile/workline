"""Tests for SecurityThreatModelingAgent schemas."""
from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    SecurityControl,
    SecurityDataFlow,
    SecurityTestCase,
    ThreatActor,
    ThreatMitigation,
    ThreatObject,
    TrustBoundary,
)

def test_asset_object_schema():
    asset = AssetObject(
        asset_id="ASSET-01",
        project_id="PROJ-01",
        name="SurrealDB Store",
        type="DATABASE",
        classification="CRITICAL",
    )
    assert asset.asset_id == "ASSET-01"
    assert asset.classification == "CRITICAL"

def test_threat_object_schema():
    threat = ThreatObject(
        threat_id="THREAT-01",
        project_id="PROJ-01",
        title="Prompt Injection Vulnerability",
        category="PROMPT_INJECTION",
        severity=4,
        likelihood=4,
        risk_score=16,
    )
    assert threat.threat_id == "THREAT-01"
    assert threat.risk_score == 16
