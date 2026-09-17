"""Tests for CLI module."""
from research_agents.cost_supply_chain.cli import parse_args


def test_parse_args(monkeypatch):
    monkeypatch.setattr("sys.argv", ["cli.py", "--project-id", "PROJ-CLI", "--volume", "2500"])
    args = parse_args()
    assert args.project_id == "PROJ-CLI"
    assert args.volume == 2500
