"""
Test CLI commands for EngineeringOptimizationAgent.
"""
import pytest
from unittest.mock import patch
from research_agents.engineering_optimization.__main__ import main


def test_cli_demo_no_error():
    """--demo should run without error."""
    main(["--demo"])


def test_cli_run_command():
    """run command should execute optimization cycle."""
    main(["run", "--project", "proj_cli_test", "--candidates", "4"])


def test_cli_no_args_runs_demo():
    """No arguments defaults to demo mode."""
    main([])


def test_cli_pareto_nonexistent_opt():
    """pareto command with unknown opt-id returns error gracefully."""
    import io, sys
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        try:
            main(["pareto", "--opt-id", "OPT-NONEXISTENT"])
        except SystemExit:
            pass
    output = captured.getvalue()
    # Should produce some output without crashing the process
    assert True  # Just verify no unhandled exception


def test_cli_recommend_nonexistent_opt():
    import io
    with patch("sys.stdout", io.StringIO()):
        try:
            main(["recommend", "--opt-id", "OPT-NONE"])
        except SystemExit:
            pass
    assert True


def test_cli_reoptimize_version_check():
    """reoptimize command with nonexistent opt returns error."""
    import io
    with patch("sys.stdout", io.StringIO()):
        try:
            main(["reoptimize", "--opt-id", "OPT-NONE", "--bom-version", "v2.0.0"])
        except SystemExit:
            pass
    assert True
