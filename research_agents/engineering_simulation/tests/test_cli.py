"""
Unit tests for EngineeringSimulationAgent CLI commands (Sections 85–93).
"""

from research_agents.engineering_simulation.__main__ import main


def test_simulation_cli_commands_and_demo(capsys):
    # 1. Demo
    main(["--demo"])
    captured = capsys.readouterr().out
    assert "Digital Twin:" in captured
    assert "Outputs Computed:" in captured

    # 2. Simulate
    main(["simulate", "--project", "proj_sar_001", "--voltage", "3.3", "--current", "150.0"])
    cap_sim = capsys.readouterr().out
    assert "Project: proj_sar_001" in cap_sim
    assert "Power Dissipation:" in cap_sim

    # 3. Scenario
    main(["scenario", "--project", "proj_sar_001", "--description", "What if load is 2x?"])
    cap_scen = capsys.readouterr().out
    assert "Scenario Created:" in cap_scen
    assert "Base Project Unchanged" in cap_scen

    # 4. Monte Carlo
    main(["monte-carlo", "--samples", "50", "--seed", "42"])
    cap_mc = capsys.readouterr().out
    assert "Monte Carlo Analysis (50 samples" in cap_mc
    assert "Mean Power:" in cap_mc
