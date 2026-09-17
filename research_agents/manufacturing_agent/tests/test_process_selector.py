"""Tests for Manufacturing Process Selection (Section 3)."""
from research_agents.manufacturing_agent.services.process_selector import ProcessSelector

def test_process_suitability_by_volume():
    selector = ProcessSelector()
    cnc_proto = selector.evaluate_process("CNC_MACHINING", "ALUMINUM_6061", volume_tier="PROTOTYPE")
    assert cnc_proto.volume_suitability == "STRONG"

    mold_proto = selector.evaluate_process("INJECTION_MOLDING", "POLYCARBONATE", volume_tier="PROTOTYPE")
    assert mold_proto.volume_suitability == "POOR"

    mold_mass = selector.evaluate_process("INJECTION_MOLDING", "POLYCARBONATE", volume_tier="MASS_PRODUCTION")
    assert mold_mass.volume_suitability == "STRONG"
