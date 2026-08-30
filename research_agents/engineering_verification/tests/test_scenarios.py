"""
Specification-mandated test scenarios for EngineeringVerificationAgent (Sections 101–113).
"""

import pytest
from research_agents.engineering_verification.agent import EngineeringVerificationAgent
from research_agents.engineering_verification.providers.mock_provider import MockVerificationProvider
from research_agents.engineering_verification.schemas import VerificationInput


@pytest.mark.asyncio
async def test_scenario_101_unexecuted_never_pass():
    """Section 101: Unexecuted test must have status NOT_EXECUTED, never PASS."""
    agent = EngineeringVerificationAgent(reasoning_provider=MockVerificationProvider())
    inp = VerificationInput(project_id="proj_sar_001")
    # Execute with empty inputs -> tests are not executed
    out = await agent.execute_verification_cycle(inp, custom_test_inputs={})

    for r in out.results:
        assert r.status == "NOT_EXECUTED"


@pytest.mark.asyncio
async def test_scenario_102_pass_within_tolerance():
    """Section 102: Measured 3.28V against 3.3V ± 0.1V yields PASS."""
    agent = EngineeringVerificationAgent(reasoning_provider=MockVerificationProvider())
    inp = VerificationInput(project_id="proj_sar_001")
    custom_inputs = {"TEST-SAR-001": {"voltage": 3.28}, "TEST-SAR-002": {"fps": 9.0}}
    out = await agent.execute_verification_cycle(inp, custom_test_inputs=custom_inputs)

    res_volt = [r for r in out.results if r.test_id == "TEST-SAR-001"][0]
    assert res_volt.status == "PASS"


@pytest.mark.asyncio
async def test_scenario_103_fail_outside_tolerance():
    """Section 103: Measured 3.7V against 3.3V ± 0.1V yields FAIL."""
    agent = EngineeringVerificationAgent(reasoning_provider=MockVerificationProvider())
    inp = VerificationInput(project_id="proj_sar_001")
    custom_inputs = {"TEST-SAR-001": {"voltage": 3.7}, "TEST-SAR-002": {"fps": 9.0}}
    out = await agent.execute_verification_cycle(inp, custom_test_inputs=custom_inputs)

    res_volt = [r for r in out.results if r.test_id == "TEST-SAR-001"][0]
    assert res_volt.status == "FAIL"


@pytest.mark.asyncio
async def test_scenario_104_hardware_unavailable_blocked():
    """Section 104: Missing hardware fixture yields BLOCKED, never PASS."""
    agent = EngineeringVerificationAgent(reasoning_provider=MockVerificationProvider())
    inp = VerificationInput(project_id="proj_sar_001")
    out = await agent.execute_verification_cycle(inp, hardware_available=False)

    for r in out.results:
        assert r.status == "BLOCKED"
