"""
Unit tests for EngineeringValidationAgent CLI development mode (Section 50).
"""

from research_agents.engineering_validation_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test SAR Drone Validation"])
    captured = capsys.readouterr().out

    assert "Project:" in captured
    assert "Requirements:" in captured
    assert "Requirements Passed:" in captured
    assert "Architecture Checks:" in captured
    assert "Electrical Checks:" in captured
    assert "Power Checks:" in captured
    assert "Interface Checks:" in captured
    assert "BOM Checks:" in captured
    assert "Procurement Checks:" in captured
    assert "Critical Failures:" in captured
    assert "FINAL VERDICT:" in captured
