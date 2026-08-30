"""
Specification-mandated test scenarios for EngineeringComplianceAgent (Sections 88–99).
"""

import pytest
from research_agents.engineering_compliance.agent import EngineeringComplianceAgent
from research_agents.engineering_compliance.providers.mock_provider import MockComplianceProvider
from research_agents.engineering_compliance.schemas import ComplianceInput


@pytest.mark.asyncio
async def test_scenario_88_valid_pass():
    """Section 88: Valid requirement, rule, artifact, and evidence yields clean PASS and ALLOW gate."""
    agent = EngineeringComplianceAgent(reasoning_provider=MockComplianceProvider())
    inp = ComplianceInput(project_id="proj_sar_001")
    out = await agent.evaluate_compliance(inp)

    assert out.summary.gate == "ALLOW"
    assert out.summary.status == "PASS"
    assert out.summary.failed == 0


@pytest.mark.asyncio
async def test_scenario_89_voltage_fail_blocks_gate():
    """Section 89: Supply voltage exceeding maximum rating causes critical FAIL and BLOCK gate."""
    agent = EngineeringComplianceAgent(reasoning_provider=MockComplianceProvider())
    custom_data = {
        "artifact_id": "component:500-0771-01",
        "supply_voltage": 5.0,
        "max_rated_voltage": 3.3,
    }
    inp = ComplianceInput(project_id="proj_sar_001", domain_filter="ELECTRICAL")
    out = await agent.evaluate_compliance(inp, custom_artifact_data=custom_data)

    assert out.summary.gate == "BLOCK"
    assert out.summary.blocking is True
    assert out.results[0].status == "FAIL"


@pytest.mark.asyncio
async def test_scenario_90_thermal_unknown_insufficient_evidence():
    """Section 90: Missing thermal limit yields UNKNOWN and INSUFFICIENT_EVIDENCE gate (never PASS)."""
    agent = EngineeringComplianceAgent(reasoning_provider=MockComplianceProvider())
    custom_data = {
        "artifact_id": "component:500-0771-01",
    }
    inp = ComplianceInput(project_id="proj_sar_001", domain_filter="THERMAL")
    out = await agent.evaluate_compliance(inp, custom_artifact_data=custom_data)

    assert out.summary.gate == "INSUFFICIENT_EVIDENCE"
    assert out.results[0].status == "UNKNOWN"


@pytest.mark.asyncio
async def test_scenario_91_conflicting_specs_review_required():
    """Section 91: Conflicting specifications yield REVIEW and REVIEW_REQUIRED gate."""
    agent = EngineeringComplianceAgent(reasoning_provider=MockComplianceProvider())
    custom_data = {
        "artifact_id": "component:500-0771-01",
        "has_conflicting_specs": True,
    }
    inp = ComplianceInput(project_id="proj_sar_001")
    out = await agent.evaluate_compliance(inp, custom_artifact_data=custom_data)

    assert out.summary.gate == "REVIEW_REQUIRED"
    assert any(r.status == "REVIEW" for r in out.results)
