"""
Unit tests for EngineeringChangeControlAgent CLI commands (Sections 50–56).
"""

from research_agents.engineering_change_control.__main__ import main


def test_change_control_cli_commands_and_demo(capsys):
    # 1. Demo
    main(["--demo"])
    captured = capsys.readouterr().out
    assert "Change Request Created:" in captured
    assert "Direct Impact:" in captured

    # 2. Create
    main([
        "create",
        "--project", "proj_sar_001",
        "--type", "COMPONENT_CHANGE",
        "--target", "500-0771-01",
        "--title", "Upgrade thermal core",
        "--description", "Swap out 2.5 for 3.5",
    ])
    cap_create = capsys.readouterr().out
    assert "Change Request Created:" in cap_create

    # 3. Rollback
    main([
        "rollback",
        "--artifact", "ARCH-001",
        "--target-version", "v1.0.0",
        "--current-version", "v2.0.0",
        "--approved-by", "lead_bob",
    ])
    cap_roll = capsys.readouterr().out
    assert "Rollback Executed:" in cap_roll
    assert "New Version Created: v3.0.0" in cap_roll
