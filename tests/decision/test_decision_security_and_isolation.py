"""Tests for Multi-tenant Project & Team Isolation."""

import pytest
from backend.workline.decision.service import DecisionService


def test_project_isolation():
    """Test 25-27: Project scoping prevents leakage across projects."""
    service = DecisionService()
    service.create_decision(
        decision_id="DEC-PROJ-A",
        project_id="proj_alpha",
        title="Alpha Decision",
        description="Alpha project decision",
    )
    service.create_decision(
        decision_id="DEC-PROJ-B",
        project_id="proj_beta",
        title="Beta Decision",
        description="Beta project decision",
    )

    alpha_list = service.list_decisions(project_id="proj_alpha")
    beta_list = service.list_decisions(project_id="proj_beta")

    assert len(alpha_list) == 1
    assert alpha_list[0].decision_id == "DEC-PROJ-A"
    assert len(beta_list) == 1
    assert beta_list[0].decision_id == "DEC-PROJ-B"
