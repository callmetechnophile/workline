"""
Unit tests for WebResearchAgent CLI development mode.
"""

from unittest.mock import patch
from research_agents.web_research_agent.__main__ import main
from research_agents.web_research_agent.schemas import (
    ExtractedEngineeringFact,
    NormalizedWebSource,
    ProjectMeta,
    WebResearchAgentOutput,
)


def test_cli_execution_with_mocked_agent(capsys):
    mock_output = WebResearchAgentOutput(
        status="success",
        project=ProjectMeta(title="Autonomous Search Drone", domain="Robotics"),
        queries_used=["GitHub Search Drone ROS2"],
        sources_found=1,
        sources_selected=1,
        sources=[
            NormalizedWebSource(
                source_id="src_101",
                title="GitHub - thermal-drone-rescue/yolov8-ros2",
                url="https://github.com/thermal-drone-rescue/yolov8-ros2",
                domain="github.com",
                source_type="github_repository",
                relevance_score=0.94,
                authority_score=0.90,
                source_tool="tavily",
                accessed_at="2026-08-30T06:00:00Z",
            )
        ],
        facts=[
            ExtractedEngineeringFact(
                fact="ROS 2 Humble package with Jetson Orin Nano deployment instructions",
                source_id="src_101",
                source_url="https://github.com/thermal-drone-rescue/yolov8-ros2",
                extraction_method="tavily",
                confidence=0.95,
                retrieved_at="2026-08-30T06:00:00Z",
                category="software",
            )
        ],
        errors=[],
    )

    with patch("research_agents.web_research_agent.__main__.WebResearchAgent.run_sync", return_value=mock_output):
        main(["--project", "Autonomous Search Drone", "--domain", "Robotics", "--max-sources", "1"])

    captured = capsys.readouterr().out
    assert "WorkflowGuide AI" in captured
    assert "WebResearchAgent" in captured
    assert "Autonomous Search Drone" in captured
    assert "github.com" in captured or "GitHub" in captured
    assert "ROS 2 Humble package" in captured
