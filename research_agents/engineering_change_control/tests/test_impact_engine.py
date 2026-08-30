"""
Unit tests for ChangeImpactEngine (Sections 13–16, 23).
"""

from research_agents.engineering_change_control.schemas import ChangeRequest
from research_agents.engineering_change_control.services.impact_engine import ChangeImpactEngine


def test_impact_engine_direct_and_indirect_analysis():
    engine = ChangeImpactEngine()

    # 1. Component Change Impact
    chg_comp = ChangeRequest(
        change_id="C1",
        project_id="p1",
        change_type="COMPONENT_CHANGE",
        title="Replace FLIR sensor",
        description="Replace 500-0643-00 with 500-0771-01",
        target_artifact="500-0771-01",
        severity="HIGH",
    )
    imp_comp = engine.analyze_change(chg_comp)
    assert len(imp_comp.direct_impact) > 0
    assert len(imp_comp.indirect_impact) > 0
    assert "BOM" in imp_comp.revalidation_required
    assert "QA" in imp_comp.revalidation_required
    assert imp_comp.human_approval_required is True

    # 2. Documentation Change (Zero Revalidation)
    chg_doc = ChangeRequest(
        change_id="C2",
        project_id="p1",
        change_type="DOCUMENTATION_CHANGE",
        title="Update README",
        description="Fix typo in installation instructions",
        target_artifact="README.md",
        severity="LOW",
    )
    imp_doc = engine.analyze_change(chg_doc)
    assert len(imp_doc.revalidation_required) == 0
    assert imp_doc.human_approval_required is False
