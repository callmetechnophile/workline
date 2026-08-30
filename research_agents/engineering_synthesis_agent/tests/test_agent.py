"""
End-to-end unit and integration tests for EngineeringSynthesisAgent (Agent #5).
"""

import pytest
from research_agents.engineering_synthesis_agent.agent import EngineeringSynthesisAgent
from research_agents.engineering_synthesis_agent.providers.mock_provider import MockEngineeringSynthesisProvider
from research_agents.engineering_synthesis_agent.schemas import (
    EngineeringSynthesisAgentInput,
    ProjectMeta,
)


@pytest.mark.asyncio
async def test_engineering_synthesis_agent_successful_run():
    agent = EngineeringSynthesisAgent(reasoning_provider=MockEngineeringSynthesisProvider())
    input_data = EngineeringSynthesisAgentInput(
        project=ProjectMeta(
            title="Autonomous Search and Rescue Drone",
            requirements=[
                "Thermal human detection on edge hardware",
                "Real-time edge inference latency under 100ms",
            ],
            constraints=["payload power <= 20 W"],
        ),
        research_papers=[
            {"paper_id": "ev_p_001", "title": "Thermal Drone Vision", "abstract": "45 FPS on Jetson Orin Nano at 15 W."}
        ],
        web_sources=[
            {"source_id": "ev_w_001", "title": "Jetson Specs", "description": "40 TOPS compute at 15 W."}
        ],
        facts=[
            {"fact": "FLIR Lepton operates at 3.3 V", "source_document": "ev_f_001"}
        ],
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert len(output.requirement_analysis) == 2
    assert len(output.technical_findings) >= 1
    assert len(output.tradeoffs) >= 1
    assert len(output.decisions) >= 1
    assert len(output.recommendations) >= 1
    assert len(output.risks) >= 1
    assert len(output.validation_requirements) >= 1
    assert len(output.experiments) >= 1
    assert len(output.traceability) >= 1
    assert output.overall_confidence > 0.70
    assert "# Engineering Synthesis & Decision Report" in output.structured_report_markdown


def test_engineering_synthesis_agent_sync_execution():
    agent = EngineeringSynthesisAgent(reasoning_provider=MockEngineeringSynthesisProvider())
    input_data = EngineeringSynthesisAgentInput(
        project=ProjectMeta(title="Sync Test SAR Drone", requirements=["Thermal detection"]),
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert len(output.decisions) >= 1


def test_engineering_synthesis_agent_empty_evidence_graceful():
    agent = EngineeringSynthesisAgent(reasoning_provider=MockEngineeringSynthesisProvider())
    input_data = EngineeringSynthesisAgentInput(
        project=ProjectMeta(title="Empty Evidence Drone", requirements=["Thermal detection"]),
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert len(output.decisions) >= 1
    assert output.requirement_analysis[0].coverage in ("weak", "unsupported")
