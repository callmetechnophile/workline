"""
Unit tests for EngineeringArchitectureAgent CLI development mode (Section 44).
"""

from research_agents.engineering_architecture_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test SAR Drone"])
    captured = capsys.readouterr().out

    assert "Project:" in captured
    assert "CLI Test SAR Drone" in captured
    assert "Architecture:" in captured
    assert "Subsystems:" in captured
    assert "Interfaces:" in captured
    assert "Power Domains:" in captured
    assert "Data Flows:" in captured
    assert "Control Flows:" in captured
    assert "Dependencies:" in captured
    assert "Architecture Risks:" in captured
    assert "Validation Requirements:" in captured
    assert "+ Architecture generated" in captured
    assert "+ Traceability generated" in captured
    assert "+ Block diagram generated" in captured
    assert "+ Architecture graph generated" in captured
