"""
Unit tests for VerificationQAAgent CLI development mode (Section 58).
"""

from research_agents.verification_qa_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test Autonomous SAR Drone QA"])
    captured = capsys.readouterr().out

    assert "Project:" in captured
    assert "Implementation:" in captured
    assert "Tasks Executed:" in captured
    assert "Tasks Verified:" in captured
    assert "Tests:" in captured
    assert "Requirements:" in captured
    assert "Security:" in captured
    assert "Architecture:" in captured
    assert "BOM:" in captured
    assert "Authorization:" in captured
    assert "FINAL VERDICT:" in captured
