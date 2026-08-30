"""
Unit tests for ProjectStateManager service (Sections 41–44).
"""

import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.state_machine import ProjectStateManager


@pytest.mark.asyncio
async def test_state_machine_transitions_and_qa_gating():
    db = SurrealDBClient()
    manager = ProjectStateManager(db)

    # Initial state
    state = await manager.get_state("proj_01")
    assert state.current_state == "research"

    # Transition to design
    s2, _ = await manager.transition_state("proj_01", "design", "Synthesis complete", "agent")
    assert s2.current_state == "design"

    # QA Verified -> verified
    s3, _ = await manager.transition_state("proj_01", "verified", "All tests passed", "qa")
    assert s3.current_state == "verified"

    # QA Failed -> blocked (Never allowed to become verified)
    s4, _ = await manager.transition_state("proj_02", "verified", "QA Failed: 2 tests failed", "qa")
    assert s4.current_state == "blocked"
