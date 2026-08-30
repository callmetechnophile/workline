"""
Unit tests for EngineeringCopilotAgent CLI commands (Sections 73–77).
"""

from research_agents.engineering_copilot.__main__ import main


def test_copilot_cli_commands_and_demo(capsys):
    # 1. Demo
    main(["--demo"])
    captured = capsys.readouterr().out
    assert "Question:" in captured
    assert "Evidence Grounded:" in captured

    # 2. Ask
    main(["ask", "--project", "proj_sar_001", "--question", "Why was this sensor chosen?"])
    cap_ask = capsys.readouterr().out
    assert "Question: Why was this sensor chosen?" in cap_ask

    # 3. Trace
    main(["trace", "--project", "proj_sar_001", "--requirement", "REQ-SAR-001"])
    cap_trace = capsys.readouterr().out
    assert "Requirement Trace: REQ-SAR-001" in cap_trace

    # 4. Impact
    main(["impact", "--project", "proj_sar_001", "--component", "500-0771-01"])
    cap_impact = capsys.readouterr().out
    assert "Component Impact: 500-0771-01" in cap_impact

    # 5. Compare
    main(["compare", "--project", "proj_sar_001", "--version-a", "V1", "--version-b", "V2"])
    cap_comp = capsys.readouterr().out
    assert "Comparison: V1 vs V2" in cap_comp

    # 6. Status
    main(["status", "--project", "proj_sar_001"])
    cap_stat = capsys.readouterr().out
    assert "Project Status: proj_sar_001" in cap_stat

    # 7. Next
    main(["next", "--project", "proj_sar_001"])
    cap_next = capsys.readouterr().out
    assert "Recommended Next Action: proj_sar_001" in cap_next
