"""
wline workflow - Workflow dispatch, creation, validation, and lifecycle inspection.

Workflows are named sequences of capability invocations. The CLI submits
them through the Control Fabric; individual agent routing happens inside.
"""

import asyncio
import json
import os
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.wline.core.errors import exit_with_error, print_json_output, ExitCode
from cli.wline.ui.output import print_error, print_info, print_success

workflow_app = typer.Typer(
    name="workflow",
    help="List, create, validate, run, and inspect engineering workflows.",
)
console = Console()

# Canonical workflow catalogue mapped to primary capability and metadata
_WORKFLOWS = {
    "simulation-study": {
        "capability": "simulation.digital_twin",
        "description": "Engineering simulation study and digital twin run",
        "target_agent": "agent.19",
        "steps": ["define_scenario", "simulation.thermal", "simulation.digital_twin"],
    },
    "design-for-manufacturability": {
        "capability": "dfm_analysis",
        "description": "DFM check, DFA optimization, and manufacturability report",
        "target_agent": "agent.24",
        "steps": ["inspect_cad", "analyze_tolerances", "dfm_analysis"],
    },
    "optimization-loop": {
        "capability": "optimization.pareto",
        "description": "Multi-objective Pareto-front design space optimization",
        "target_agent": "agent.20",
        "steps": ["optimization.constraints", "sample_candidates", "optimization.pareto"],
    },
    "threat-model": {
        "capability": "security.stride",
        "description": "Full cyber-physical system threat modelling pass (STRIDE/PASTA)",
        "target_agent": "agent.22",
        "steps": ["map_architecture", "security.stride", "security.threat_matrix"],
    },
    "tech-documentation": {
        "capability": "create_document",
        "description": "Technical documentation generation and specification authoring",
        "target_agent": "agent.27",
        "steps": ["compile_specs", "create_document", "review_document"],
    },
    "evidence-synthesis": {
        "capability": "research.synthesize",
        "description": "Evidence chain synthesis and technical research aggregation",
        "target_agent": "agent.04",
        "steps": ["research.papers", "extract_claims", "research.synthesize"],
    },
    "compliance-audit": {
        "capability": "compliance.audit_trail",
        "description": "Engineering compliance and regulatory requirements audit",
        "target_agent": "agent.17",
        "steps": ["compliance.standards_check", "compliance.audit_trail"],
    },
}


def _fabric():
    from armourflow.fabric.fabric import get_control_fabric
    return get_control_fabric()


@workflow_app.command("list")
def workflow_list(
    json_output: bool = typer.Option(False, "--json", help="Output workflows catalogue as pure JSON"),
):
    """Show all available named workflows and their primary capabilities."""
    if json_output:
        res = [
            {
                "name": name,
                "capability": meta["capability"],
                "target_agent": meta["target_agent"],
                "description": meta["description"],
                "steps": meta["steps"],
            }
            for name, meta in _WORKFLOWS.items()
        ]
        print_json_output({"workflows": res, "total": len(res)})
        return

    table = Table(title="Available Workflows", border_style="cyan")
    table.add_column("Workflow Name", style="bold cyan")
    table.add_column("Primary Capability", style="yellow")
    table.add_column("Target Agent", style="dim")
    table.add_column("Description", style="white")

    for wf_name, meta in _WORKFLOWS.items():
        table.add_row(wf_name, meta["capability"], meta["target_agent"], meta["description"])

    console.print(table)
    print_info("Run: wline workflow run <name> [--payload '{...}']")


@workflow_app.command("create")
def workflow_create(
    name: str = typer.Argument(..., help="New workflow name"),
    capability: str = typer.Option(..., "--capability", "-c", help="Primary capability to bind"),
    description: str = typer.Option("Custom user workflow", "--description", "-d", help="Workflow description"),
    json_output: bool = typer.Option(False, "--json", help="Output creation result as pure JSON"),
):
    """Register a custom workflow definition into the active workspace."""
    clean_name = name.strip().lower()
    _WORKFLOWS[clean_name] = {
        "capability": capability,
        "description": description,
        "target_agent": "dynamic",
        "steps": [capability],
    }

    if json_output:
        print_json_output({
            "name": clean_name,
            "capability": capability,
            "description": description,
            "status": "REGISTERED",
        })
        return

    print_success(f"Workflow '{clean_name}' created and registered with capability '{capability}'.")


@workflow_app.command("validate")
def workflow_validate(
    name: str = typer.Argument(..., help="Workflow name to validate"),
    json_output: bool = typer.Option(False, "--json", help="Output validation result as pure JSON"),
):
    """Validate that a workflow definition has valid capabilities and agent bindings."""
    clean_name = name.strip().lower()
    if clean_name not in _WORKFLOWS:
        exit_with_error(
            f"Workflow '{name}' not found. Available workflows: {', '.join(_WORKFLOWS.keys())}",
            code=ExitCode.INVALID_ARGUMENTS,
            json_mode=json_output,
        )

    meta = _WORKFLOWS[clean_name]
    from armourflow.registry.registry import get_agent_registry
    reg = get_agent_registry()
    providers = reg.find_by_capability(meta["capability"])

    valid = len(providers) > 0
    validation_res = {
        "workflow": clean_name,
        "valid": valid,
        "capability": meta["capability"],
        "providing_agents": [p.agent_id for p in providers],
        "steps_count": len(meta["steps"]),
    }

    if json_output:
        print_json_output(validation_res)
        return

    if valid:
        print_success(f"Workflow '{clean_name}' is VALID. Capability '{meta['capability']}' is provided by: {', '.join(p.agent_id for p in providers)}")
    else:
        exit_with_error(
            f"Workflow '{clean_name}' validation failed: No registered agent provides capability '{meta['capability']}'.",
            code=ExitCode.VALIDATION_FAILURE,
            json_mode=False,
        )


@workflow_app.command("run")
def workflow_run(
    name: str = typer.Argument(..., help="Workflow name (e.g. 'simulation-study')"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="JSON context payload for workflow"),
    json_output: bool = typer.Option(False, "--json", help="Output run results as pure JSON"),
):
    """Dispatch a named workflow through the Agent Control Fabric."""
    clean_name = name.strip().lower()
    if clean_name not in _WORKFLOWS:
        exit_with_error(
            f"Unknown workflow '{name}'. Known workflows: {', '.join(_WORKFLOWS.keys())}",
            code=ExitCode.INVALID_ARGUMENTS,
            json_mode=json_output,
        )

    meta = _WORKFLOWS[clean_name]
    capability = meta["capability"]

    raw = payload.strip()
    if raw.startswith("@") and os.path.exists(raw[1:]):
        with open(raw[1:], encoding="utf-8") as f:
            raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        exit_with_error("Payload must be valid JSON.", code=ExitCode.INVALID_ARGUMENTS, json_mode=json_output)

    if not json_output:
        console.print(f"[bold cyan]Dispatching workflow:[/] {clean_name}  → capability: {capability}")
        console.print(f"[dim]{meta['description']}[/]")

    fabric = _fabric()
    try:
        task = asyncio.run(
            fabric.submit_task(
                payload={"workflow": clean_name, **data},
                target_capability=capability,
                project_id=project,
            )
        )
    except Exception as e:
        exit_with_error(f"Workflow execution failed: {e}", code=ExitCode.SERVICE_UNAVAILABLE, json_mode=json_output)

    if json_output:
        print_json_output(task.model_dump())
        return

    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"\nTask: [bold cyan]{task.task_id}[/]  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Workflow Result", border_style="green"))


@workflow_app.command("status")
def workflow_status(
    workflow_id: str = typer.Argument(..., help="Workflow task ID returned from 'wline workflow run'"),
    json_output: bool = typer.Option(False, "--json", help="Output workflow task status as pure JSON"),
):
    """Check the state and output of a running or completed workflow task."""
    fabric = _fabric()
    t = fabric.get_task(workflow_id)
    if not t:
        exit_with_error(f"Workflow task '{workflow_id}' not found.", code=ExitCode.INVALID_ARGUMENTS, json_mode=json_output)

    if json_output:
        print_json_output(t.model_dump())
        return

    color = "green" if t.state.value == "COMPLETED" else "yellow"
    console.print(f"Workflow Task: [bold cyan]{t.task_id}[/]  State: [{color}]{t.state.value}[/]")
    console.print(f"Capability: [bold white]{t.target_capability}[/]  Project: [dim]{t.context.project_id}[/]")

    if t.result:
        console.print(Panel(json.dumps(t.result, indent=2, default=str), title="Workflow Output", border_style="green"))
    elif t.error:
        console.print(f"[bold red]Error:[/] {t.error}")


@workflow_app.command("history")
def workflow_history(
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum workflow tasks to display"),
    json_output: bool = typer.Option(False, "--json", help="Output workflow history as pure JSON"),
):
    """List workflow execution history for a project."""
    fabric = _fabric()
    all_tasks = fabric.list_tasks(project)
    # Filter tasks that were triggered with workflow metadata or capabilities
    wf_tasks = [t for t in all_tasks if "workflow" in t.payload or t.target_capability in [m["capability"] for m in _WORKFLOWS.values()]][:limit]

    if json_output:
        print_json_output({
            "project_id": project,
            "workflow_tasks": [t.model_dump() for t in wf_tasks],
            "total": len(wf_tasks),
        })
        return

    if not wf_tasks:
        print_info(f"No workflow runs found for project '{project}'.")
        return

    table = Table(title=f"Workflow History – project '{project}' ({len(wf_tasks)} recorded)", border_style="cyan")
    table.add_column("Task ID", style="bold cyan", no_wrap=True)
    table.add_column("Workflow / Cap", style="white")
    table.add_column("State", justify="center")
    table.add_column("Created", style="dim")

    for t in wf_tasks:
        wf_name = t.payload.get("workflow", t.target_capability or "-")
        color = "green" if t.state.value == "COMPLETED" else "yellow"
        table.add_row(t.task_id, str(wf_name), f"[{color}]{t.state.value}[/]", str(t.created_at)[:19])

    console.print(table)
