"""
Unit tests for EngineeringSynthesisAgent CLI development mode (Section 35).
"""

from research_agents.engineering_synthesis_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test Drone"])
    captured = capsys.readouterr().out

    assert "Project:" in captured
    assert "CLI Test Drone" in captured
    assert "Requirements:" in captured
    assert "Technical Findings:" in captured
    assert "Trade-offs:" in captured
    assert "Engineering Decisions:" in captured
    assert "Recommendations:" in captured
    assert "Risks:" in captured
    assert "Validation Requirements:" in captured
    assert "Overall Confidence:" in captured
    assert "+ Evidence traceability generated" in captured
    assert "+ Engineering decisions generated" in captured
    assert "+ Validation plan generated" in captured
