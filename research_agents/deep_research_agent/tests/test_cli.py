"""
Unit tests for DeepResearchAgent CLI development mode.
"""

from research_agents.deep_research_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test Drone", "--domain", "Robotics"])
    captured = capsys.readouterr().out

    assert "WorkflowGuide AI" in captured
    assert "DeepResearchAgent" in captured
    assert "CLI Test Drone" in captured
    assert "Executive Engineering Summary" in captured
    assert "Component Trade Studies" in captured
    assert "Synthesized Claims" in captured
    assert "Actionable Engineering Recommendations" in captured
