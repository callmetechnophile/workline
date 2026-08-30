"""
End-to-end unit and integration tests for EngineeringKnowledgeGraphAgent (Agent #13).
"""

import pytest
from research_agents.engineering_knowledge_graph_agent.agent import EngineeringKnowledgeGraphAgent
from research_agents.engineering_knowledge_graph_agent.providers.mock_provider import MockGraphProvider
from research_agents.engineering_knowledge_graph_agent.schemas import EngineeringKnowledgeGraphInput


@pytest.mark.asyncio
async def test_engineering_knowledge_graph_agent_full_run():
    agent = EngineeringKnowledgeGraphAgent(reasoning_provider=MockGraphProvider())

    input_data = EngineeringKnowledgeGraphInput(
        project={"title": "Autonomous SAR Drone", "project_id": "proj_sar_001"},
        requirements=[{"requirement_id": "REQ-01", "description": "Thermal 15 FPS"}],
        architecture={"subsystems": ["ThermalImagingSubsystem"]},
        bom={"items": [{"component_id": "500-0771-01", "name": "FLIR Lepton"}]},
        verification_qa={"verdict": "VERIFIED"},
    )

    output = await agent.run(input_data)
    assert output.status == "success"
    assert output.current_state == "verified"
    assert output.nodes_created > 0
    assert output.relationships_created > 0
    assert "# Engineering Project Knowledge Graph" in output.structured_report_markdown


def test_engineering_knowledge_graph_agent_sync_and_adk_capabilities():
    agent = EngineeringKnowledgeGraphAgent(reasoning_provider=MockGraphProvider())

    input_data = EngineeringKnowledgeGraphInput(
        project={"title": "SAR Drone Sync", "project_id": "proj_sar_sync"},
        verification_qa={"verdict": "VERIFIED"},
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"

    # ADK Capability checks
    graph = agent.query_project_graph("proj_sar_sync", "user_001")
    assert graph["project_id"] == "proj_sar_sync"

    trace = agent.trace_requirement("REQ-SAR-001", "proj_sar_sync", "user_001")
    assert trace.requirement_id == "REQ-SAR-001"

    impact = agent.analyze_impact("500-0771-01", "proj_sar_sync", "user_001")
    assert impact.part_number == "500-0771-01"

    timeline = agent.get_project_timeline("proj_sar_sync", "user_001")
    assert len(timeline) >= 4
