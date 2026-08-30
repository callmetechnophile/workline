"""
Unit tests for EngineeringExecutionAgent CLI development mode (Section 56).
"""

from research_agents.engineering_execution_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test SAR Drone Execution"])
    captured = capsys.readouterr().out

    assert "Project:" in captured
    assert "Validation:" in captured
    assert "Authorized Tasks:" in captured
    assert "Authorization:" in captured
    assert "ArmorIQ:" in captured
    assert "Executing:" in captured
    assert "TASK-001" in captured
    assert "TASK-002" in captured
