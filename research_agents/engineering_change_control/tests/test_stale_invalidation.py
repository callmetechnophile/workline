"""
Unit tests for stale artifact propagation and QA result invalidation (Sections 24 & 25).
"""

from research_agents.engineering_change_control.schemas import ChangeRequest
from research_agents.engineering_change_control.services.impact_engine import ChangeImpactEngine


def test_stale_and_invalidation_marking():
    engine = ChangeImpactEngine()

    chg = ChangeRequest(
        change_id="C_ARCH_01",
        project_id="p1",
        change_type="ARCHITECTURE_CHANGE",
        title="Revise SPI interface",
        description="Upgrade VoSPI interface to 15 FPS",
        target_artifact="ARCH-001",
        severity="HIGH",
    )

    impact = engine.analyze_change(chg)

    # Stale artifacts marked without deletion
    assert len(impact.stale_artifacts) > 0
    assert any("task" in s for s in impact.stale_artifacts)

    # QA result invalidated
    assert len(impact.invalidated_artifacts) > 0
    assert any("qa_verdict" in inv for inv in impact.invalidated_artifacts)
