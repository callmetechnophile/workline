"""Tests for CLI Argument Parser."""
from research_agents.manufacturing_agent.cli import build_parser

def test_cli_parser():
    parser = build_parser()
    assert parser.prog == "manufacturing_agent"
