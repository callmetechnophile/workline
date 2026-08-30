"""
Unit tests for CLI test runner and terminal table formatting.
"""

from unittest.mock import patch
from research_agents.research_paper_agent.__main__ import main
from research_agents.research_paper_agent.schemas import (
    NormalizedPaper,
    ProjectMeta,
    ResearchPaperAgentOutput,
)


def test_cli_execution_with_mocked_agent(capsys):
    mock_output = ResearchPaperAgentOutput(
        status="success",
        project=ProjectMeta(title="Autonomous Search Drone", domain="Robotics"),
        queries_used=["thermal vision UAV"],
        papers_found=1,
        papers_selected=1,
        papers=[
            NormalizedPaper(
                paper_id="paper_101",
                title="Thermal Human Detection for UAVs",
                authors=["Jane Doe"],
                publication_date="2024",
                doi="10.1109/UAV.101",
                source="freephdlabor",
                paper_url="https://example.com/paper/101",
                pdf_url="https://example.com/paper/101.pdf",
                pdf_available=True,
                relevance_score=0.92,
                relevance_reasons=["Direct thermal detection"],
            )
        ],
        errors=[],
    )

    with patch("research_agents.research_paper_agent.__main__.ResearchPaperAgent.run_sync", return_value=mock_output):
        main(["--project", "Autonomous Search Drone", "--domain", "Robotics", "--max-papers", "1"])

    captured = capsys.readouterr().out
    assert "WorkflowGuide AI" in captured
    assert "Autonomous Search Drone" in captured
    assert "Thermal Human" in captured
    assert "YES" in captured
    assert "freephdlabor" in captured

