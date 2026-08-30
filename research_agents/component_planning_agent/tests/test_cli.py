"""
Unit tests for ComponentPlanningAgent CLI development mode (Section 45).
"""

from research_agents.component_planning_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test SAR Drone"])
    captured = capsys.readouterr().out

    assert "Project:" in captured
    assert "BOM Line Items:" in captured
    assert "Selected:" in captured
    assert "Candidates:" in captured
    assert "Pending:" in captured
    assert "Subsystems:" in captured
    assert "Compatibility Issues:" in captured
    assert "Alternatives:" in captured
    assert "Validation Requirements:" in captured
    assert "+ BOM generated" in captured
    assert "+ Compatibility checked" in captured
    assert "+ Alternatives generated" in captured
    assert "+ Traceability generated" in captured
