"""
tests/cli/test_wline_canonical.py

Canonical wline CLI smoke-test suite.

Verifies that all 12 user-facing canonical commands from the implementation
plan are registered, importable, and return exit-code 0 (or an acceptable
non-zero) when called with --help or lightweight arguments.

These tests use Typer's CliRunner so no real I/O or network calls are made.
"""

import pytest
from typer.testing import CliRunner
from cli.wline.main import app

runner = CliRunner()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def invoke_help(*args: str):
    """Invoke a command with --help and assert it exits 0."""
    result = runner.invoke(app, list(args) + ["--help"])
    assert result.exit_code == 0, (
        f"Command {list(args)} --help exited {result.exit_code}\nOutput:\n{result.output}"
    )
    return result


# ──────────────────────────────────────────────────────────────────────────────
# 1. Top-level banner / help
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_top_level_help():
    """wline --help must exit 0 and mention all new command groups."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Core platform groups must appear in help output
    for cmd in ["agents", "task", "workflow", "engineering", "evidence",
                "documents", "security", "eval", "system"]:
        assert cmd in result.output, f"'{cmd}' missing from wline --help output"


def test_wline_no_args_banner():
    """wline with no args shows the banner (exit 0)."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    # Should mention both sections
    assert "agents" in result.output.lower() or "WORKLINE" in result.output or "wline" in result.output.lower()


# ──────────────────────────────────────────────────────────────────────────────
# 2. wline init
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_init_help():
    invoke_help("init")


# ──────────────────────────────────────────────────────────────────────────────
# 3. wline project list
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_project_list_help():
    invoke_help("project", "list")


# ──────────────────────────────────────────────────────────────────────────────
# 4. wline agents list / inspect / health / capabilities
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_agents_help():
    invoke_help("agents")

def test_wline_agents_list_help():
    invoke_help("agents", "list")

def test_wline_agents_inspect_help():
    invoke_help("agents", "inspect")

def test_wline_agents_health_help():
    invoke_help("agents", "health")

def test_wline_agents_capabilities_help():
    invoke_help("agents", "capabilities")

def test_wline_agents_list_runs():
    """wline agents list should instantiate the registry and print a table."""
    result = runner.invoke(app, ["agents", "list"])
    # Acceptable outcomes: success (0) or registry initialisation messages
    assert result.exit_code == 0, f"agents list failed: {result.output}"
    # Either a table header or agent count
    assert "agent" in result.output.lower() or "ID" in result.output or "registry" in result.output.lower()


# ──────────────────────────────────────────────────────────────────────────────
# 5. wline task run / create / list / status / cancel
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_task_help():
    invoke_help("task")

def test_wline_task_run_help():
    invoke_help("task", "run")

def test_wline_task_create_help():
    invoke_help("task", "create")

def test_wline_task_list_help():
    invoke_help("task", "list")

def test_wline_task_status_help():
    invoke_help("task", "status")

def test_wline_task_cancel_help():
    invoke_help("task", "cancel")

def test_wline_task_run_no_args_exits_nonzero():
    """wline task run without --agent or --capability should exit 1."""
    result = runner.invoke(app, ["task", "run"])
    assert result.exit_code != 0 or "Specify" in result.output


# ──────────────────────────────────────────────────────────────────────────────
# 6. wline workflow run / list / status
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_workflow_help():
    invoke_help("workflow")

def test_wline_workflow_list_help():
    invoke_help("workflow", "list")

def test_wline_workflow_run_help():
    invoke_help("workflow", "run")

def test_wline_workflow_status_help():
    invoke_help("workflow", "status")

def test_wline_workflow_list_runs():
    """wline workflow list should print the workflow catalogue."""
    result = runner.invoke(app, ["workflow", "list"])
    assert result.exit_code == 0
    assert "simulation-study" in result.output or "Workflow" in result.output


# ──────────────────────────────────────────────────────────────────────────────
# 7. wline engineering simulation / optimize / dfm
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_engineering_help():
    invoke_help("engineering")

def test_wline_engineering_simulation_help():
    invoke_help("engineering", "simulation")

def test_wline_engineering_optimize_help():
    invoke_help("engineering", "optimize")

def test_wline_engineering_dfm_help():
    invoke_help("engineering", "dfm")


# ──────────────────────────────────────────────────────────────────────────────
# 8. wline evidence search / inspect
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_evidence_help():
    invoke_help("evidence")

def test_wline_evidence_search_help():
    invoke_help("evidence", "search")

def test_wline_evidence_inspect_help():
    invoke_help("evidence", "inspect")


# ──────────────────────────────────────────────────────────────────────────────
# 9. wline documents generate / list / review
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_documents_help():
    invoke_help("documents")

def test_wline_documents_generate_help():
    invoke_help("documents", "generate")

def test_wline_documents_list_help():
    invoke_help("documents", "list")

def test_wline_documents_review_help():
    invoke_help("documents", "review")


# ──────────────────────────────────────────────────────────────────────────────
# 10. wline graph query / traverse
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_graph_help():
    invoke_help("graph")

def test_wline_graph_query_help():
    invoke_help("graph", "query")

def test_wline_graph_traverse_help():
    invoke_help("graph", "traverse")

def test_wline_graph_related_help():
    """Existing graph related command must still be accessible."""
    invoke_help("graph", "related")


# ──────────────────────────────────────────────────────────────────────────────
# 11. wline security audit / scan
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_security_help():
    invoke_help("security")

def test_wline_security_audit_help():
    invoke_help("security", "audit")

def test_wline_security_scan_help():
    invoke_help("security", "scan")


# ──────────────────────────────────────────────────────────────────────────────
# 12. wline eval run / report
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_eval_help():
    invoke_help("eval")

def test_wline_eval_run_help():
    invoke_help("eval", "run")

def test_wline_eval_report_help():
    invoke_help("eval", "report")


# ──────────────────────────────────────────────────────────────────────────────
# 13. wline system health / status / diagnostics
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_system_help():
    invoke_help("system")

def test_wline_system_health_help():
    invoke_help("system", "health")

def test_wline_system_status_help():
    invoke_help("system", "status")

def test_wline_system_diagnostics_help():
    invoke_help("system", "diagnostics")

def test_wline_system_health_runs():
    """wline system health should print a health table."""
    result = runner.invoke(app, ["system", "health"])
    assert result.exit_code == 0, f"system health failed:\n{result.output}"
    # Must mention at least one component
    assert any(
        kw in result.output
        for kw in ["Control Fabric", "HEALTHY", "Platform", "Agent Registry", "Model Provider"]
    )

def test_wline_system_status_runs():
    """wline system status should show the platform status panel."""
    result = runner.invoke(app, ["system", "status"])
    assert result.exit_code == 0, f"system status failed:\n{result.output}"
    assert any(kw in result.output for kw in ["WORKLINE", "ArmourFlow", "Platform", "Environment"])


# ──────────────────────────────────────────────────────────────────────────────
# 14. Backwards compat – existing commands must still work
# ──────────────────────────────────────────────────────────────────────────────

def test_wline_agent_singular_help():
    """wline agent (singular, internal runtime) must still be accessible."""
    invoke_help("agent")

def test_wline_version_help():
    invoke_help("version")

def test_wline_git_help():
    invoke_help("git")

def test_wline_project_help():
    invoke_help("project")
