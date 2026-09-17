"""Tests for CLI Module."""
from research_agents.security_threat.cli import build_parser

def test_cli_parser():
    parser = build_parser()
    assert parser.prog == "security_threat"
