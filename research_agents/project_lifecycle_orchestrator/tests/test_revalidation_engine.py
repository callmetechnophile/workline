"""
Unit tests for RevalidationEngine (Sections 34–37).
"""

from research_agents.project_lifecycle_orchestrator.services.revalidation_engine import RevalidationEngine


def test_revalidation_scope_and_stale_markers():
    engine = RevalidationEngine()

    # 1. Documentation change requires ZERO revalidation
    p_doc = engine.determine_revalidation_scope("DOCUMENTATION", "README.md")
    assert len(p_doc.required_stages) == 0
    assert p_doc.human_approval_needed is False

    # 2. Firmware change requires QA only
    p_fw = engine.determine_revalidation_scope("FIRMWARE", "firmware/sensors/lepton.py")
    assert "QA" in p_fw.required_stages

    # 3. Architecture change requires full downstream + human approval
    p_arch = engine.determine_revalidation_scope("ARCHITECTURE", "ARCH-01")
    assert "ARCHITECTURE" in p_arch.required_stages
    assert p_arch.human_approval_needed is True

    # 4. Stale items generated without deletion
    stale_items = engine.mark_stale_artifacts(p_arch)
    assert len(stale_items) > 0
    assert any(s.status == "invalidated" for s in stale_items)
