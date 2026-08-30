"""
Unit tests for RequirementValidator (Sections 9 & 10).
"""

from research_agents.engineering_validation_agent.services.requirement_validator import RequirementValidator


def test_requirement_validation_coverage():
    validator = RequirementValidator()

    synth = {
        "requirements": [
            {"requirement_id": "REQ-01", "description": "Thermal human detection at 15 FPS."},
            {"requirement_id": "REQ-02", "description": "Edge neural inference on Jetson."},
        ]
    }
    arch = {"subsystems": [{"name": "Thermal Sensing"}, {"name": "Edge Compute"}]}
    bom = {
        "items": [
            {"part_number": "500-0771-01", "category": "thermal camera"},
            {"part_number": "900-13766-0000-000", "category": "SBC"},
        ]
    }
    proc = {"optimized_items": [{"bom_item_id": "BOM-01"}]}

    results = validator.validate_requirements(synth, arch, bom, proc)
    assert len(results) == 2
    assert all(r.status == "PASS" for r in results)
    assert all(r.coverage == "STRONG" for r in results)
