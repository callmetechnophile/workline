"""Tests for Attack Surface and Trust Boundary Mapping."""
from research_agents.security_threat.services.attack_surface_engine import AttackSurfaceEngine

def test_discover_assets():
    engine = AttackSurfaceEngine()
    assets = engine.discover_assets("PROJ-TEST")
    assert len(assets) >= 4
    categories = [a.category for a in assets]
    assert "GRAPH_DATA" in categories
    assert "TOKENS" in categories

def test_map_trust_boundaries():
    engine = AttackSurfaceEngine()
    tbs = engine.map_trust_boundaries()
    assert len(tbs) >= 4
    ids = [tb.boundary_id for tb in tbs]
    assert "TB-PUBLIC-API" in ids
    assert "TB-FABRIC-EXEC" in ids

def test_map_attack_surface():
    engine = AttackSurfaceEngine()
    entries = engine.map_attack_surface()
    assert len(entries) >= 4
    types = [e.type for e in entries]
    assert "AUTH" in types
    assert "A2A" in types
