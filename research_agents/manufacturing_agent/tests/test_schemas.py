"""Tests for Manufacturing / DFM-DFA schemas."""
from research_agents.manufacturing_agent.schemas import (
    CostDriverHandoff,
    DFAModel,
    DFMFinding,
    InspectionItem,
    ManufacturingProcess,
    ManufacturingReadiness,
    ManufacturingRecommendation,
    ToleranceItem,
    ToolingRequirement,
    VariationData,
)

def test_manufacturing_process_schema():
    p = ManufacturingProcess(
        process_id="P-01",
        name="CNC Milling",
        family="CNC_MACHINING",
        tolerance_capability="STRONG",
    )
    assert p.process_id == "P-01"
    assert p.tolerance_capability == "STRONG"

def test_dfm_finding_schema():
    f = DFMFinding(
        finding_id="DFM-01",
        component_id="BRACKET",
        category="FEATURE_ACCESSIBILITY",
        severity="MAJOR",
        description="Deep cavity aspect ratio exceeds 4:1",
    )
    assert f.finding_id == "DFM-01"
    assert f.severity == "MAJOR"

def test_cost_driver_schema():
    cd = CostDriverHandoff(
        project_id="PROJ-01",
        component_id="BRACKET",
        process_family="CNC_MACHINING",
        part_count_impact="1 unit",
        setup_count_estimate=2,
    )
    assert cd.setup_count_estimate == 2
