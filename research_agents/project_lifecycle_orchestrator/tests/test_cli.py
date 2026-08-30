"""
Unit tests for ProjectLifecycleOrchestrator CLI commands (Sections 60–66).
"""

from research_agents.project_lifecycle_orchestrator.__main__ import main


def test_cli_commands_and_demo(capsys):
    # 1. Demo
    main(["--demo"])
    captured = capsys.readouterr().out
    assert "Project:" in captured
    assert "State:" in captured
    assert "Next Action:" in captured

    # 2. Status
    main(["status", "--project", "PROJECT-001"])
    cap_status = capsys.readouterr().out
    assert "Project:" in cap_status
    assert "State:" in cap_status

    # 3. Next (Verified)
    main(["next", "--project", "PROJECT-001", "--qa-status", "VERIFIED"])
    cap_next = capsys.readouterr().out
    assert "Recommended Next Action:" in cap_next

    # 4. Next (Failed)
    main(["next", "--project", "PROJECT-001", "--qa-status", "FAILED", "--failure-type", "TEST_FAILURE"])
    cap_next_f = capsys.readouterr().out
    assert "Target:" in cap_next_f

    # 5. Health
    main(["health", "--project", "PROJECT-001"])
    cap_health = capsys.readouterr().out
    assert "Project Health:" in cap_health

    # 6. Blockers
    main(["blockers", "--project", "PROJECT-001"])
    cap_blk = capsys.readouterr().out
    assert "Active Blockers:" in cap_blk

    # 7. Impact
    main(["impact", "--change-type", "DOCUMENTATION", "--artifact", "README.md"])
    cap_imp = capsys.readouterr().out
    assert "Revalidation Scope" in cap_imp
    assert "NONE (Zero engineering revalidation)" in cap_imp
