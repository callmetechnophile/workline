"""Tests for DFM Engine (Section 1)."""
from research_agents.manufacturing_agent.services.dfm_engine import DFMEngine

def test_deep_cavity_detection():
    engine = DFMEngine()
    comp = {
        "component_id": "BRACKET-01",
        "intended_process": "CNC_MACHINING",
        "pocket_depth_mm": 50.0,
        "pocket_corner_radius_mm": 5.0,  # 10:1 ratio
    }
    findings = engine.analyze_component(comp)
    assert any(f.category == "FEATURE_ACCESSIBILITY" for f in findings)

def test_thin_wall_sheet_metal():
    engine = DFMEngine()
    comp = {
        "component_id": "ENCLOSURE",
        "intended_process": "SHEET_METAL",
        "wall_thickness_mm": 0.4,  # Below 0.6mm
    }
    findings = engine.analyze_component(comp)
    assert any(f.category == "WALL_THICKNESS" for f in findings)

def test_cast_iron_sheet_metal_mismatch():
    engine = DFMEngine()
    comp = {
        "component_id": "BASE_PLATE",
        "material": "GRAY_CAST_IRON",
        "intended_process": "SHEET_METAL_BENDING",
    }
    findings = engine.analyze_component(comp)
    assert any(f.category == "MATERIAL_PROCESS_MISMATCH" and f.severity == "BLOCKER" for f in findings)
