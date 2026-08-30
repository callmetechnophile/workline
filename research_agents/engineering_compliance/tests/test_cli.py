"""
Unit tests for EngineeringComplianceAgent CLI commands (Sections 80–86).
"""

from research_agents.engineering_compliance.__main__ import main


def test_compliance_cli_commands_and_demo(capsys):
    # 1. Demo
    main(["--demo"])
    captured = capsys.readouterr().out
    assert "Project Compliance Summary:" in captured
    assert "Gate Outcome:" in captured

    # 2. Check
    main(["check", "--project", "proj_sar_001"])
    cap_chk = capsys.readouterr().out
    assert "Project: proj_sar_001" in cap_chk
    assert "Gate:" in cap_chk

    # 3. Matrix
    main(["matrix", "--project", "proj_sar_001"])
    cap_mat = capsys.readouterr().out
    assert "Traceability Matrix:" in cap_mat
    assert "Requirement" in cap_mat

    # 4. Waiver
    main([
        "waiver",
        "--project", "proj_sar_001",
        "--rule", "RULE-ELEC-01",
        "--artifact", "component:500-0771-01",
        "--reason", "Lab variance",
        "--approved-by", "safety_officer",
    ])
    cap_waiv = capsys.readouterr().out
    assert "Waiver Created:" in cap_waiv
