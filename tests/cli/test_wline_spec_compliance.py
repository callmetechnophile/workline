"""
Specification compliance tests for WORKLINE CLI (wline).

Tests:
- wline --help, wline --version
- wline init --help
- wline system: status, health, version (--json and human-readable)
- wline project: list, inspect, status (--json and human-readable)
- wline task: create, run, status, cancel, history (--json and human-readable)
- wline workflow: list, create, validate, run, status, history (--json and human-readable)
- Output cleanliness (no banners/ANSI in JSON)
- Deterministic exit codes
"""

import json
from typer.testing import CliRunner

from cli.wline.main import app
from cli.wline.core.errors import ExitCode

runner = CliRunner()


# ──────────────────────────────────────────────────────────────────────────────
# Foundation: Help and Version
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "WORKLINE" in result.output
    # Check core subcommands in help output
    for cmd in ["init", "project", "agents", "task", "workflow", "system"]:
        assert cmd in result.output


def test_wline_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_wline_init_help():
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize" in result.output


# ──────────────────────────────────────────────────────────────────────────────
# System Commands
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_system_status():
    result = runner.invoke(app, ["system", "status"])
    assert result.exit_code == 0
    assert "WORKLINE" in result.output
    assert "Control Fabric" in result.output


def test_wline_system_status_json():
    result = runner.invoke(app, ["system", "status", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "WORKLINE" in data["platform"]
    assert data["registered_agents"] == 27
    assert "control_fabric" in data


def test_wline_system_health():
    result = runner.invoke(app, ["system", "health"])
    assert result.exit_code == 0
    assert "Control Fabric" in result.output


def test_wline_system_health_json():
    result = runner.invoke(app, ["system", "health", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "components" in data
    assert len(data["components"]) >= 4


def test_wline_system_version_json():
    result = runner.invoke(app, ["system", "version", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "cli_version" in data


# ──────────────────────────────────────────────────────────────────────────────
# Project Commands
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_project_list():
    result = runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0


def test_wline_project_list_json():
    result = runner.invoke(app, ["project", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "projects" in data


def test_wline_project_inspect_nonexistent():
    result = runner.invoke(app, ["project", "inspect", "nonexistent-project"])
    assert result.exit_code == int(ExitCode.INVALID_ARGUMENTS)


def test_wline_project_inspect_nonexistent_json():
    result = runner.invoke(app, ["project", "inspect", "nonexistent-project", "--json"])
    assert result.exit_code == int(ExitCode.INVALID_ARGUMENTS)
    data = json.loads(result.output)
    assert data["status"] == "error"


# ──────────────────────────────────────────────────────────────────────────────
# Task Commands
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_task_create_and_status():
    result = runner.invoke(app, [
        "task", "create",
        "--agent", "agent.24",
        "--capability", "dfm_analysis",
        "--payload", '{"component": "bracket"}',
    ])
    assert result.exit_code == 0
    assert "Task created:" in result.output or "Task ID:" in result.output

    # Extract task ID from JSON output to test status
    json_res = runner.invoke(app, [
        "task", "create",
        "--agent", "agent.24",
        "--capability", "dfm_analysis",
        "--payload", '{"component": "bracket"}',
        "--json",
    ])
    assert json_res.exit_code == 0
    data = json.loads(json_res.output)
    task_id = data["task_id"]

    # Now check status
    status_res = runner.invoke(app, ["task", "status", task_id])
    assert status_res.exit_code == 0
    assert task_id in status_res.output

    # Status JSON
    status_json_res = runner.invoke(app, ["task", "status", task_id, "--json"])
    assert status_json_res.exit_code == 0
    stat_data = json.loads(status_json_res.output)
    assert stat_data["task_id"] == task_id


def test_wline_task_cancel():
    # Create task
    json_res = runner.invoke(app, [
        "task", "create",
        "--agent", "agent.19",
        "--capability", "simulate_component",
        "--payload", '{"scenario": "thermal"}',
        "--json",
    ])
    data = json.loads(json_res.output)
    task_id = data["task_id"]

    # Cancel task
    cancel_res = runner.invoke(app, ["task", "cancel", task_id, "--json"])
    assert cancel_res.exit_code == 0
    cancel_data = json.loads(cancel_res.output)
    assert cancel_data["task_id"] == task_id


def test_wline_task_history():
    result = runner.invoke(app, ["task", "history"])
    assert result.exit_code == 0


def test_wline_task_history_json():
    result = runner.invoke(app, ["task", "history", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "tasks" in data


def test_wline_task_run_missing_args():
    result = runner.invoke(app, ["task", "run"])
    assert result.exit_code == int(ExitCode.INVALID_ARGUMENTS)


# ──────────────────────────────────────────────────────────────────────────────
# Workflow Commands
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_workflow_list():
    result = runner.invoke(app, ["workflow", "list"])
    assert result.exit_code == 0
    assert "simulation-study" in result.output


def test_wline_workflow_list_json():
    result = runner.invoke(app, ["workflow", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "workflows" in data
    assert len(data["workflows"]) >= 5


def test_wline_workflow_validate():
    result = runner.invoke(app, ["workflow", "validate", "simulation-study"])
    assert result.exit_code == 0
    assert "VALID" in result.output


def test_wline_workflow_validate_json():
    result = runner.invoke(app, ["workflow", "validate", "simulation-study", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["valid"] is True
    assert data["workflow"] == "simulation-study"


def test_wline_workflow_create():
    result = runner.invoke(app, [
        "workflow", "create", "custom-qa-flow",
        "--capability", "qa.lint",
        "--description", "Automated QA lint flow",
    ])
    assert result.exit_code == 0
    assert "custom-qa-flow" in result.output


def test_wline_workflow_run_and_status():
    result = runner.invoke(app, [
        "workflow", "run", "simulation-study",
        "--payload", '{"component": "heatsink"}',
        "--json",
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    wf_task_id = data["task_id"]

    status_res = runner.invoke(app, ["workflow", "status", wf_task_id, "--json"])
    assert status_res.exit_code == 0
    stat_data = json.loads(status_res.output)
    assert stat_data["task_id"] == wf_task_id


def test_wline_workflow_history():
    result = runner.invoke(app, ["workflow", "history"])
    assert result.exit_code == 0


def test_wline_workflow_history_json():
    result = runner.invoke(app, ["workflow", "history", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "workflow_tasks" in data
