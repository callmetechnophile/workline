"""End-to-End integration test: Multi-Agent delegation from Google ADK to external agents."""

import pytest
from backend.workline.agents.interoperability_tools import (
    cancel_external_task,
    delegate_external_task,
    discover_external_agents,
    get_external_capabilities,
    get_external_task_status,
)
from backend.workline.interoperability.selection import AgentSelectionService
from backend.workline.knowledge.service import knowledge_service


@pytest.mark.asyncio
async def test_e2e_thermal_agent_delegation_flow():
    # 1. Internal Google ADK agent discovers external capabilities
    discovered = discover_external_agents(capability_type="THERMAL_ANALYSIS")
    assert len(discovered) >= 1
    assert any(a["agent_id"] == "ThermalSolver" for a in discovered)

    # 2. Inspect target agent capabilities
    caps = get_external_capabilities("ThermalSolver")
    thermal_cap = next((c for c in caps if c["capability_id"] == "thermal_simulation"), None)
    assert thermal_cap is not None

    # 3. Agent selection ranks best candidate
    selected = AgentSelectionService.select_agent_for_capability("thermal_simulation")
    assert selected is not None
    agent, rank_score = selected
    assert agent.agent_id == "ThermalSolver"
    assert rank_score > 0.0

    # 4. Delegate task through Interoperability Gateway
    task_dict = await delegate_external_task(
        project_id="test_e2e_rover",
        team_id="team_engineering",
        requesting_agent="PCBAgent",
        target_agent="ThermalSolver",
        capability="thermal_simulation",
        payload={
            "board_width": 100.0,
            "board_height": 80.0,
            "ambient_temp": 25.0,
            "components": [
                {"name": "U1_Regulator", "power_dissipation_watts": 2.5},
                {"name": "U2_MCU", "power_dissipation_watts": 0.4},
            ],
        },
        idempotency_key="e2e-idemp-thermal-001",
        human_approved=True,
    )

    # 5. Verify task completion, output schema, and provenance
    assert task_dict["status"] == "COMPLETED"
    assert task_dict["provenance"] is not None
    assert task_dict["output_reference"]["max_temperature"] > 50.0

    # 6. Verify task status lookup
    status_lookup = get_external_task_status(task_dict["task_id"])
    assert status_lookup is not None
    assert status_lookup["status"] == "COMPLETED"

    # 7. Verify sync to Engineering Knowledge as proposal / finding
    findings = knowledge_service.list_findings("test_e2e_rover")
    assert len(findings) >= 1
    assert any("ThermalSolver" in f.title or "thermal" in f.title.lower() for f in findings)
