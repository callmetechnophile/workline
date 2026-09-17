"""Tests for CLI module."""
from research_agents.engineering_risk.cli import main

def test_cli_import():
    import research_agents.engineering_risk.cli as cli_mod
    assert hasattr(cli_mod, "main")
