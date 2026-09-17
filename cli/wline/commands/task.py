"""
wline task - Task submission, routing, and lifecycle management.

All task operations route through AgentControlFabric. The CLI never
directly imports or executes any domain agent.
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
from cli.wline.ui.output import print_error, print_success, print_info

task_app = typer.Typer(name="task", help="Submit, inspect, cancel, and audit Control Fabric tasks.")
console = Console()


def _fabric():
    from armourflow.fabric.fabric import get_control_fabric
    return get_control_fabric()


def _parse_payload(payload: str, json_output: bool = False) -> dict:
    raw = payload.strip()
    if raw.startswith("@") and os.path.exists(raw[1:]):
        with open(raw[1:], encoding="utf-8") as f:
            raw = f.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            import ast
            data = ast.literal_eval(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        exit_with_error(f"Invalid JSON payload: {raw[:80]}", ExitCode.INVALID_ARGUMENTS, json_mode=json_output)


@task_app.command("run")
def task_run(
    task_id: Optional[str] = typer.Argument(None, help="Task ID to execute, or target agent/capability via options"),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Target agent ID (e.g. 'agent.24', '14')"),
    capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Target capability name"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="JSON task payload string or @filepath"),
    json_output: bool = typer.Option(False, "--json", help="Output task execution result as pure JSON"),
):
    """Submit or run a task through the Control Fabric and display the result."""
    fabric = _fabric()

    # If an existing task_id is provided, check if it's already queued/cached
    if task_id and not agent and not capability:
        t = fabric.get_task(task_id)
        if not t:
            exit_with_error(f"Task '{task_id}' not found.", ExitCode.INVALID_ARGUMENTS, json_mode=json_output)
        # If task exists, report its status/result
        if json_output:
            print_json_output(t.model_dump())
            return
        color = "green" if t.state.value == "COMPLETED" else "yellow"
        console.print(f"Task ID: [bold cyan]{t.task_id}[/]  Agent: [bold white]{t.target_agent_id}[/]  State: [{color}]{t.state.value}[/]")
        if t.result:
            console.print(Panel(json.dumps(t.result, indent=2, default=str), title="Result", border_style="green"))
        return

    if not agent and not capability:
        exit_with_error(
            "Specify either --agent <agent-id> or --capability <name>.",
            ExitCode.INVALID_ARGUMENTS,
            json_mode=json_output,
        )

    # Normalize agent ID if provided
    target_agent = None
    if agent:
        from cli.wline.commands.agents import normalize_agent_id
        target_agent = normalize_agent_id(agent)

    data = _parse_payload(payload, json_output=json_output)

    try:
        task = asyncio.run(
            fabric.submit_task(
                payload=data,
                target_agent_id=target_agent,
                target_capability=capability,
                project_id=project,
            )
        )
    except Exception as e:
        exit_with_error(f"Task submission failed: {e}", ExitCode.SERVICE_UNAVAILABLE, json_mode=json_output)

    if json_output:
        print_json_output(task.model_dump())
        return

    color = "green" if task.state.value == "COMPLETED" else ("yellow" if task.state.value in ("PENDING", "EXECUTING") else "red")
    console.print(
        f"Task ID: [bold cyan]{task.task_id}[/]  "
        f"Agent: [bold white]{task.target_agent_id}[/]  "
        f"State: [{color}]{task.state.value}[/]"
    )
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Result", border_style="green"))


@task_app.command("create")
def task_create(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Target agent ID"),
    capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Target capability name"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="JSON task payload string or @filepath"),
    json_output: bool = typer.Option(False, "--json", help="Output created task as pure JSON"),
):
    """Create and submit a task to the Control Fabric."""
    if not agent and not capability:
        exit_with_error(
            "Specify either --agent <agent-id> or --capability <name>.",
            ExitCode.INVALID_ARGUMENTS,
            json_mode=json_output,
        )

    target_agent = None
    if agent:
        from cli.wline.commands.agents import normalize_agent_id
        target_agent = normalize_agent_id(agent)

    data = _parse_payload(payload, json_output=json_output)
    fabric = _fabric()

    try:
        task = asyncio.run(
            fabric.submit_task(
                payload=data,
                target_agent_id=target_agent,
                target_capability=capability,
                project_id=project,
            )
        )
    except Exception as e:
        exit_with_error(f"Failed to create task: {e}", ExitCode.SERVICE_UNAVAILABLE, json_mode=json_output)

    if json_output:
        print_json_output(task.model_dump())
        return

    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"[bold green]Task created:[/] {task.task_id}  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Result", border_style="green"))


@task_app.command("status")
def task_status(
    task_id: str = typer.Argument(..., help="Task ID to inspect"),
    json_output: bool = typer.Option(False, "--json", help="Output task status as pure JSON"),
):
    """Display lifecycle state and output of a submitted task."""
    fabric = _fabric()
    t = fabric.get_task(task_id)
    if not t:
        exit_with_error(f"Task '{task_id}' not found.", ExitCode.INVALID_ARGUMENTS, json_mode=json_output)

    if json_output:
        print_json_output(t.model_dump())
        return

    color = "green" if t.state.value == "COMPLETED" else ("yellow" if t.state.value in ("PENDING", "EXECUTING") else "red")
    console.print(f"Task: [bold cyan]{t.task_id}[/]  State: [{color}]{t.state.value}[/]")
    console.print(f"Agent: [bold white]{t.target_agent_id}[/]  Project: [dim]{t.context.project_id}[/]")
    console.print(f"Created: [dim]{str(t.created_at)[:19]}[/]  Updated: [dim]{str(t.updated_at)[:19]}[/]")

    if t.result:
        console.print(Panel(json.dumps(t.result, indent=2, default=str), title="Task Result", border_style="green"))
    elif t.error:
        console.print(f"[bold red]Error:[/] {t.error}")


@task_app.command("cancel")
def task_cancel(
    task_id: str = typer.Argument(..., help="Task ID to cancel"),
    json_output: bool = typer.Option(False, "--json", help="Output cancel result as pure JSON"),
):
    """Request cancellation of a queued or running task."""
    fabric = _fabric()
    t = fabric.get_task(task_id)
    if not t:
        exit_with_error(f"Task '{task_id}' not found.", ExitCode.INVALID_ARGUMENTS, json_mode=json_output)

    from armourflow.fabric.schemas import TaskState
    if t.state.value in ("COMPLETED", "FAILED", "CANCELLED"):
        if json_output:
            print_json_output({"task_id": task_id, "state": t.state.value, "message": "Already terminal"})
            return
        print_info(f"Task already in terminal state: {t.state.value}")
        return

    t.state = TaskState.CANCELLED
    if json_output:
        print_json_output({"task_id": task_id, "state": "CANCELLED", "success": True})
    else:
        print_success(f"Task {task_id} marked as CANCELLED.")


@task_app.command("history")
@task_app.command("list", hidden=True)
def task_history(
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum entries to display"),
    json_output: bool = typer.Option(False, "--json", help="Output task history as pure JSON"),
):
    """Display task execution history and audit logs for a project."""
    fabric = _fabric()
    tasks = fabric.list_tasks(project)[:limit]

    if json_output:
        print_json_output({
            "project_id": project,
            "tasks": [t.model_dump() for t in tasks],
            "total": len(tasks),
        })
        return

    if not tasks:
        print_info(f"No task history found for project '{project}'.")
        return

    table = Table(title=f"Task History – project '{project}' ({len(tasks)} recorded)", border_style="cyan")
    table.add_column("Task ID", style="bold cyan", no_wrap=True)
    table.add_column("Agent", style="white")
    table.add_column("Capability", style="dim")
    table.add_column("State", justify="center")
    table.add_column("Created", style="dim")

    for t in tasks:
        color = "green" if t.state.value == "COMPLETED" else (
            "yellow" if t.state.value in ("PENDING", "EXECUTING") else "red"
        )
        table.add_row(
            t.task_id,
            t.target_agent_id or "-",
            t.target_capability or "-",
            f"[{color}]{t.state.value}[/]",
            str(t.created_at)[:19],
        )

    console.print(table)
