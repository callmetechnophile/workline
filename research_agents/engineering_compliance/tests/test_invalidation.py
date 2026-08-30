"""
Unit tests for compliance result invalidation upon upstream component changes (Sections 47–50, 92).
"""

import pytest
from research_agents.engineering_compliance.repository.compliance_repository import ComplianceRepository
from research_agents.engineering_compliance.schemas import ComplianceResult


@pytest.mark.asyncio
async def test_compliance_result_invalidation():
    repo = ComplianceRepository()

    res = ComplianceResult(
        compliance_id="COMPL-001",
        project_id="p1",
        artifact_id="component:500-0643-00",
        artifact_type="component",
        domain="ELECTRICAL",
        status="PASS",
        severity="HIGH",
        rule_id="RULE-ELEC-01",
        description="Lepton 2.5 passed voltage check.",
    )
    await repo.create_result(res)
    assert res.status == "PASS"

    # Upstream change invalidates old result (Section 49 & 92)
    inv = await repo.invalidate_result("COMPL-001")
    assert inv is not None
    assert inv.status == "INVALIDATED"
