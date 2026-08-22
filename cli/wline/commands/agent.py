"""Agent commands for Workline CLI."""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.workline.agents.runtime import agent_runtime
from backend.workline.agents.shared.state import AgentStatus
from cli.wline.core.paths import get_active_project_name
from cli.wline.ui.output import print_error, print_info, print_success, print_warning

agent_app = typer.Typer(name="agent", help="Manage and inspect Workline Multi-Agent Engine executions.")
console = Console()


@agent_app.command("status")
def agent_status() -> None:
    """Inspect active agent, lifecycle stage, and execution status."""
    active_name = get_active_project_name()
    if not active_name:
        print_error("No active project selected. Run 'wline project open <name>' or create one.")
        raise typer.Exit(code=1)

    console.print("\n[bold cyan]WORKLINE AGENTS[/bold cyan]\n")
    console.print(f"[bold white]Project:[/bold white] [bold green]{active_name}[/bold green]")

    execs = agent_runtime.list_executions_for_project(active_name)
    if not execs:
        console.print("[yellow]Status:[/yellow]  IDLE")
        console.print("[yellow]Agent:[/yellow]   None\n")
        return

    latest = execs[-1]
    status_color = "green" if latest.status == AgentStatus.COMPLETED else ("yellow" if latest.status in (AgentStatus.RUNNING, AgentStatus.WAITING_FOR_USER) else "red")

    console.print(f"[bold white]Current:[/bold white]   {latest.agent_id.replace('_', ' ').title()}")
    console.print(f"[bold white]Status:[/bold white]    [{status_color}]{latest.status.value}[/{status_color}]")
    console.print(f"[bold white]Stage:[/bold white]     {latest.stage.replace('_', ' ').title()}")

    if latest.requires_user_action:
        console.print(f"\n[bold yellow]! ACTION REQUIRED:[/bold yellow] {latest.action_prompt}")
        console.print("[dim]Run 'wline agent approve START_BUILD' or 'wline agent approve CONTINUE_RESEARCH'[/dim]\n")
    else:
        console.print()


@agent_app.command("run")
def agent_run(
    task: str = typer.Argument(..., help="Task or problem description for the multi-agent engine."),
    stage: Optional[str] = typer.Option(None, "--stage", "-s", help="Optional target lifecycle stage."),
) -> None:
    """Launch multi-agent workflow for the active project."""
    active_name = get_active_project_name()
    if not active_name:
        print_error("No active project selected. Run 'wline project open <name>' or 'wline init'.")
        raise typer.Exit(code=1)

    console.print(f"\n[bold cyan]Launching Workline Multi-Agent Engine for:[/bold cyan] [bold green]{active_name}[/bold green]\n")
    print_info(f"Task: {task}")

    state = asyncio.run(
        agent_runtime.start_execution(
            project_id=active_name,
            task=task,
            stage=stage or "ideation",
        )
    )

    if state.status == AgentStatus.WAITING_FOR_USER:
        print_success("Planning & Research Phase Completed!")
        console.print(f"\n[bold yellow]{state.action_prompt}[/bold yellow]")
        console.print("[cyan]•[/cyan] Run [bold green]wline agent approve START_BUILD[/bold green] to continue hardware engineering.")
        console.print("[cyan]•[/cyan] Run [bold green]wline agent approve CONTINUE_RESEARCH[/bold green] for further investigation.\n")
    elif state.status == AgentStatus.COMPLETED:
        print_success(f"Agent Execution Completed: {state.output_summary}\n")
    else:
        print_error(f"Agent Execution State: {state.status.value}")


@agent_app.command("approve")
def agent_approve(
    decision: str = typer.Argument(..., help="Decision action: START_BUILD or CONTINUE_RESEARCH"),
) -> None:
    """Respond to a human decision checkpoint."""
    active_name = get_active_project_name()
    if not active_name:
        print_error("No active project selected.")
        raise typer.Exit(code=1)

    execs = agent_runtime.list_executions_for_project(active_name)
    waiting = [e for e in execs if e.status == AgentStatus.WAITING_FOR_USER]
    if not waiting:
        print_error("No executions are currently waiting for user approval.")
        raise typer.Exit(code=1)

    target_exec = waiting[-1]
    console.print(f"\n[bold cyan]Submitting Decision:[/bold cyan] [bold green]{decision.upper()}[/bold green]...")

    state = asyncio.run(
        agent_runtime.submit_human_approval(
            execution_id=target_exec.execution_id,
            decision=decision.upper(),
        )
    )

    if state.status == AgentStatus.COMPLETED:
        print_success(f"Hardware Build Tree Completed! {state.output_summary}\n")
    elif state.status == AgentStatus.WAITING_FOR_USER:
        print_info(f"Updated: {state.action_prompt}\n")
    else:
        print_info(f"Execution updated to: {state.status.value}\n")


@agent_app.command("history")
def agent_history() -> None:
    """View recent execution events and state transitions."""
    active_name = get_active_project_name()
    if not active_name:
        print_error("No active project selected.")
        raise typer.Exit(code=1)

    execs = agent_runtime.list_executions_for_project(active_name)
    if not execs:
        print_info("No agent history for active project.")
        return

    table = Table(title=f"AGENT EXECUTION HISTORY ({active_name})", box=None)
    table.add_column("Timestamp", style="dim")
    table.add_column("Agent", style="cyan")
    table.add_column("Event Type", style="yellow")
    table.add_column("Summary", style="white")

    for exc in execs:
        for ev in exc.events[-10:]:
            table.add_row(ev.timestamp[:19], ev.agent_id, ev.event_type, ev.summary[:60])

    console.print(table)
    console.print()
