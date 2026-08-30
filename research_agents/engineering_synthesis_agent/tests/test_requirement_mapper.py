"""
Unit tests for RequirementMapper service.
"""

from research_agents.engineering_synthesis_agent.schemas import ProjectMeta
from research_agents.engineering_synthesis_agent.services.requirement_mapper import RequirementMapper


def test_requirement_mapping_coverage_evaluation():
    mapper = RequirementMapper()
    project = ProjectMeta(
        title="SAR Drone",
        requirements=[
            "Thermal human detection on edge compute",
            "Long endurance flight >= 60 min",
        ],
    )
    evidence = [
        {"evidence_id": "ev_01", "text": "Thermal detection with YOLOv8 on Jetson."},
        {"evidence_id": "ev_02", "text": "Human detection benchmark using infrared sensors."},
    ]

    analyses = mapper.map_requirements(project, evidence, technical_finding_ids=["FIND-001"])

    assert len(analyses) == 2

    # First requirement should have strong coverage (matches both thermal and human)
    assert analyses[0].requirement_id == "REQ-001"
    assert analyses[0].coverage == "strong"
    assert analyses[0].evidence_count >= 2
    assert "ev_01" in analyses[0].supporting_evidence_ids

    # Second requirement has weak/unsupported coverage (no battery/endurance evidence)
    assert analyses[1].requirement_id == "REQ-002"
    assert analyses[1].coverage in ("weak", "unsupported")
