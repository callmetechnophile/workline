"""
Unit tests for EngineeringVerificationAgent CLI commands (Sections 85–92).
"""

from research_agents.engineering_verification.__main__ import main


def test_verification_cli_commands_and_demo(capsys):
    # 1. Demo
    main(["--demo"])
    captured = capsys.readouterr().out
    assert "Verification Plan:" in captured
    assert "Measurements Recorded:" in captured

    # 2. Status
    main(["status", "--project", "proj_sar_001"])
    cap_stat = capsys.readouterr().out
    assert "Project: proj_sar_001" in cap_stat
    assert "Verification Coverage:" in cap_stat

    # 3. Coverage
    main(["coverage", "--project", "proj_sar_001"])
    cap_cov = capsys.readouterr().out
    assert "Verification Coverage for proj_sar_001:" in cap_cov

    # 4. Matrix
    main(["matrix", "--project", "proj_sar_001"])
    cap_mat = capsys.readouterr().out
    assert "Requirement Verification Matrix:" in cap_mat
    assert "Requirement" in cap_mat

    # 5. Reverify
    main(["reverify", "--project", "proj_sar_001", "--target", "sensor_core"])
    cap_rev = capsys.readouterr().out
    assert "Re-verification Scope for change on 'sensor_core':" in cap_rev
