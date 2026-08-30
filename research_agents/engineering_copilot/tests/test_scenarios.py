"""
Mandated specification test scenarios for EngineeringCopilotAgent (Sections 82–95).
"""

import pytest
from research_agents.engineering_copilot.agent import EngineeringCopilotAgent
from research_agents.engineering_copilot.providers.mock_provider import MockCopilotProvider
from research_agents.engineering_copilot.schemas import CopilotInput


@pytest.mark.asyncio
async def test_scenario_82_requirement_trace():
    """Section 82: Requirement trace query returns complete graph lineage."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="Trace REQ-SAR-001", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert resp.intent == "REQUIREMENT_TRACE"
    assert "REQ-SAR-001" in resp.answer
    assert "Traceability Lineage" in resp.answer


@pytest.mark.asyncio
async def test_scenario_83_component_impact():
    """Section 83: Component replacement query returns impact graph without tool execution."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="What happens if 500-0771-01 is replaced?", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert resp.intent == "COMPONENT_IMPACT"
    assert "Direct Impact" in resp.answer
    assert "Revalidation Required" in resp.answer


@pytest.mark.asyncio
async def test_scenario_84_project_blocked():
    """Section 84: Querying why project is blocked returns actual blocker from graph."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="Why is the project blocked?", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert resp.intent == "FAILURE_QUERY"
    assert "Blocker Details" in resp.answer


@pytest.mark.asyncio
async def test_scenario_85_next_action():
    """Section 85: Querying next action delegates to Agent #14 without inventing lifecycle state."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="What should happen next?", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert resp.intent == "NEXT_ACTION"
    assert "Recommended Next Action" in resp.answer


@pytest.mark.asyncio
async def test_scenario_86_action_request_creates_proposal():
    """Section 86: Action command creates ActionProposal without direct execution."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="Run TASK-042", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert resp.intent == "ACTION_REQUEST"
    assert resp.action_proposal is not None
    assert resp.action_proposal.requested_action == "Run TASK-042"


@pytest.mark.asyncio
async def test_scenario_89_unknown_data():
    """Section 89: Querying unverified property returns UNKNOWN rather than hallucination."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="What is the maximum operating temperature?", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert "UNKNOWN:" in resp.answer


@pytest.mark.asyncio
async def test_scenario_90_stale_architecture():
    """Section 90: Unvalidated draft V3 is identified as STALE over validated V2."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="Show architecture V3 unvalidated draft", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert "Architecture V2.0.0 is the active validated architecture" in resp.answer
    assert "STALE" in resp.answer


@pytest.mark.asyncio
async def test_scenario_93_armoriq_boundary():
    """Section 93: User requests 'Modify firmware' -> ActionProposal with authorization required."""
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())
    inp = CopilotInput(message="Modify firmware sensors", project_id="proj_sar_001")
    resp = await copilot.answer(inp)

    assert resp.action_proposal is not None
    assert resp.action_proposal.requires_authorization is True
