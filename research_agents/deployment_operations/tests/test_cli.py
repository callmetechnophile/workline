"""Tests for CLI module."""
from research_agents.deployment_operations.cli import parse_args


def test_cli_parsing(monkeypatch):
    monkeypatch.setattr("sys.argv", ["cli.py", "--project-id", "PROJ-CLI", "--system-id", "SYS-CLI", "--system-type", "PHYSICAL"])
    args = parse_args()
    assert args.project_id == "PROJ-CLI"
    assert args.system_id == "SYS-CLI"
    assert args.system_type == "PHYSICAL"
