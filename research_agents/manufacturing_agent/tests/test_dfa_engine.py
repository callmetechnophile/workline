"""Tests for DFA Engine (Section 2)."""
from research_agents.manufacturing_agent.services.dfa_engine import DFAEngine

def test_excessive_fastener_count():
    engine = DFAEngine()
    assy = {
        "assembly_id": "GEARBOX_COVER",
        "part_count": 4,
        "fastener_count": 18,
    }
    model = engine.analyze_assembly(assy)
    assert any(f.category == "FASTENER_COUNT" for f in model.findings)

def test_orientation_ambiguity_and_poka_yoke():
    engine = DFAEngine()
    assy = {
        "assembly_id": "MOTOR_MOUNT",
        "orientation_ambiguity": True,
    }
    model = engine.analyze_assembly(assy)
    amb_finding = next((f for f in model.findings if f.category == "ORIENTATION_AMBIGUITY"), None)
    assert amb_finding is not None
    assert amb_finding.proposed_poka_yoke is not None
