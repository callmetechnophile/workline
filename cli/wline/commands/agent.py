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


from backend.workline.interoperability.capabilities import (
    AgentCapability,
    AgentStatus as ExtAgentStatus,
    RiskLevel,
)
from backend.workline.interoperability.gateway import interoperability_gateway
from backend.workline.interoperability.registry import ExternalAgent, agent_registry


@agent_app.command("status")
def agent_status(
    task_id: Optional[str] = typer.Argument(None, help="Optional external task ID to inspect."),
) -> None:
    """Inspect active internal agent execution or external task status."""
    if task_id:
        # Inspect external task
        task = interoperability_gateway.get_task(task_id)
        if not task:
            print_error(f"External task '{task_id}' not found.")
            raise typer.Exit(code=1)

        console.print("\n[bold cyan]WORKLINE EXTERNAL AGENT TASK[/bold cyan]\n")
        console.print(f"[bold white]TASK ID:[/bold white]     [bold green]{task.task_id}[/bold green]")
        console.print(f"[bold white]Agent:[/bold white]       {task.target_agent}")
        console.print(f"[bold white]Capability:[/bold white]  {task.capability}")
        console.print(f"[bold white]Status:[/bold white]      [bold yellow]{task.status.value}[/bold yellow]")
        console.print(f"[bold white]Risk Level:[/bold white]  {task.risk_level.value}")
        console.print(f"[bold white]Created:[/bold white]     {task.created_at[:19]}")
        if task.started_at:
            console.print(f"[bold white]Started:[/bold white]     {task.started_at[:19]}")
        if task.completed_at:
            console.print(f"[bold white]Completed:[/bold white]   {task.completed_at[:19]}")
        if task.provenance:
            console.print(f"[bold white]Duration:[/bold white]    {task.provenance.execution_duration}s")
            console.print(f"[bold white]Output Hash:[/bold white] {task.provenance.output_hash[:16]}...")
        if task.error:
            console.print(f"[bold red]Error:[/bold red]       {task.error}")
        console.print()
        return

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


@agent_app.command("list")
def agent_list(
    protocol: Optional[str] = typer.Option(None, "--protocol", "-p", help="Filter by protocol (e.g. BINDU_A2A, CORSAIR)"),
) -> None:
    """List registered external agents and their protocols."""
    agents = agent_registry.list_agents()
    if protocol:
        agents = [a for a in agents if a.protocol.upper() == protocol.upper()]

    if not agents:
        print_info("No registered external agents found.")
        return

    table = Table(title="REGISTERED EXTERNAL AGENTS", box=None)
    table.add_column("Agent ID", style="bold cyan")
    table.add_column("Protocol", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Version", style="white")
    table.add_column("Trust", style="magenta")
    table.add_column("Capabilities", style="dim")

    for ag in agents:
        trust = agent_registry.get_trust_record(ag.agent_id)
        caps = ", ".join(c.capability_id for c in ag.capabilities)
        table.add_row(
            ag.agent_id,
            ag.protocol,
            ag.status.value,
            ag.version,
            f"{trust.trust_score:.2f}",
            caps[:40] + ("..." if len(caps) > 40 else ""),
        )

    console.print(table)
    console.print()


@agent_app.command("discover")
def agent_discover(
    protocol: Optional[str] = typer.Option(None, "--protocol", "-p", help="Filter by protocol"),
    capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Filter by capability"),
) -> None:
    """Discover available external agents across Bindu, Corsair, and network providers."""
    agents = agent_registry.discover_agents(protocol=protocol, capability_type=capability, force_refresh=True)

    console.print("\n[bold cyan]EXTERNAL AGENTS[/bold cyan]\n")
    if not agents:
        print_info("No external agents discovered matching the criteria.")
        return

    for ag in agents:
        console.print(f"[bold green]{ag.name}[/bold green]")
        console.print(f"Protocol: [cyan]{ag.protocol.replace('_', ' ')}[/cyan]")
        console.print(f"Status:   [yellow]{ag.status.value}[/yellow]")
        console.print(f"Provider: {ag.provider}")
        console.print("Capabilities:")
        for c in ag.capabilities:
            console.print(f"  - [bold white]{c.capability_id}[/bold white]: {c.description} [dim](Risk: {c.risk_level.value}, Cost: ${c.estimated_cost:.2f})[/dim]")
        console.print()


@agent_app.command("info")
def agent_info(
    agent_id: str = typer.Argument(..., help="ID of the agent to inspect"),
) -> None:
    """Display comprehensive details, trust score, and metadata for an agent."""
    ag = agent_registry.get_agent(agent_id)
    if not ag:
        print_error(f"External agent '{agent_id}' not found.")
        raise typer.Exit(code=1)

    trust = agent_registry.get_trust_record(agent_id)

    console.print(f"\n[bold cyan]AGENT DETAILS: {ag.name}[/bold cyan]\n")
    console.print(f"[bold white]Agent ID:[/bold white]      {ag.agent_id}")
    console.print(f"[bold white]Provider:[/bold white]      {ag.provider}")
    console.print(f"[bold white]Protocol:[/bold white]      {ag.protocol}")
    console.print(f"[bold white]Endpoint:[/bold white]      {ag.endpoint or 'None'}")
    console.print(f"[bold white]Version:[/bold white]       {ag.version}")
    console.print(f"[bold white]Status:[/bold white]        [yellow]{ag.status.value}[/yellow]")
    console.print(f"[bold white]Trust Score:[/bold white]   [magenta]{trust.trust_score:.2f}[/magenta] [dim]({trust.successful_tasks} success / {trust.failed_tasks} fail / {trust.timeouts} timeout)[/dim]")
    console.print(f"[bold white]Description:[/bold white]   {ag.description}\n")


@agent_app.command("capabilities")
def agent_capabilities(
    agent_id: str = typer.Argument(..., help="ID of the agent to query"),
) -> None:
    """List declared capabilities and risk profiles for an external agent."""
    ag = agent_registry.get_agent(agent_id)
    if not ag:
        print_error(f"External agent '{agent_id}' not found.")
        raise typer.Exit(code=1)

    table = Table(title=f"CAPABILITIES: {ag.name}", box=None)
    table.add_column("Capability ID", style="bold cyan")
    table.add_column("Name", style="white")
    table.add_column("Risk Level", style="yellow")
    table.add_column("Cost (USD)", style="green")
    table.add_column("Description", style="dim")

    for c in ag.capabilities:
        table.add_row(
            c.capability_id,
            c.name,
            c.risk_level.value,
            f"${c.estimated_cost:.2f}",
            c.description[:50],
        )

    console.print(table)
    console.print()


@agent_app.command("register")
def agent_register(
    agent_id: str = typer.Option(..., "--id", help="Agent identifier"),
    name: str = typer.Option(..., "--name", help="Display name"),
    protocol: str = typer.Option("BINDU_A2A", "--protocol", help="Protocol: BINDU_A2A or CORSAIR"),
    endpoint: Optional[str] = typer.Option(None, "--endpoint", help="Endpoint URI"),
    description: str = typer.Option("Custom external agent", "--desc", help="Description"),
) -> None:
    """Register a new external agent with Workline."""
    agent = ExternalAgent(
        agent_id=agent_id,
        name=name,
        description=description,
        protocol=protocol.upper(),
        endpoint=endpoint,
    )
    agent_registry.register_agent(agent)
    print_success(f"Successfully registered external agent '{agent.agent_id}' ({agent.protocol})")


@agent_app.command("unregister")
def agent_unregister(
    agent_id: str = typer.Argument(..., help="ID of the agent to unregister"),
) -> None:
    """Unregister an external agent from Workline."""
    if agent_registry.unregister_agent(agent_id):
        print_success(f"Successfully unregistered external agent '{agent_id}'")
    else:
        print_error(f"External agent '{agent_id}' not found.")
        raise typer.Exit(code=1)


@agent_app.command("task")
def agent_task(
    agent_id: str = typer.Argument(..., help="Target external agent ID (e.g. ThermalSolver)"),
    capability: str = typer.Argument(..., help="Capability name (e.g. thermal_simulation)"),
    team_id: str = typer.Option("default_team", "--team", "-t", help="Team ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip interactive confirmation"),
) -> None:
    """Submit an engineering subtask to an external agent."""
    active_name = get_active_project_name()
    if not active_name:
        print_error("No active project selected. Run 'wline project open <name>' or 'wline init'.")
        raise typer.Exit(code=1)

    ag = agent_registry.get_agent(agent_id)
    if not ag:
        print_error(f"External agent '{agent_id}' not found.")
        raise typer.Exit(code=1)

    cap = next((c for c in ag.capabilities if c.capability_id == capability), None)
    risk_str = cap.risk_level.value if cap else "LOW"

    console.print("\n[bold cyan]WORKLINE EXTERNAL AGENT TASK[/bold cyan]\n")
    console.print(f"[bold white]Agent:[/bold white]         [bold green]{ag.name}[/bold green]")
    console.print(f"[bold white]Capability:[/bold white]    {capability}")
    console.print(f"[bold white]Risk:[/bold white]          {risk_str}")
    console.print(f"[bold white]Project:[/bold white]       {active_name}")
    console.print(f"[bold white]Authorization:[/bold white] [bold green]VALID[/bold green]\n")

    if not confirm:
        should_submit = typer.confirm("Submit task?", default=True)
        if not should_submit:
            print_info("Task submission cancelled.")
            return

    console.print("\n[dim]Delegating task to Interoperability Gateway...[/dim]")
    task = asyncio.run(
        interoperability_gateway.submit_task(
            project_id=active_name,
            team_id=team_id,
            requesting_agent="WorklineCLI",
            target_agent_id=agent_id,
            capability_id=capability,
            payload={"board_width": 100.0, "board_height": 80.0, "components": [{"name": "U1", "power_dissipation_watts": 1.2}]},
            human_approved=True,
        )
    )

    if task.status.value == "COMPLETED":
        print_success(f"Task {task.task_id} completed successfully in {task.provenance.execution_duration}s!")
        console.print(f"[bold white]Result:[/bold white] {task.output_reference}\n")
    elif task.status.value == "REJECTED":
        print_error(f"Task {task.task_id} rejected: {task.error}")
    else:
        print_info(f"Task {task.task_id} status: {task.status.value}")


@agent_app.command("cancel")
def agent_cancel(
    task_id: str = typer.Argument(..., help="External task ID to cancel"),
) -> None:
    """Cancel an active external agent task."""
    success = asyncio.run(interoperability_gateway.cancel_task(task_id))
    if success:
        print_success(f"Task '{task_id}' cancelled.")
    else:
        print_error(f"Could not cancel task '{task_id}'. Task may not exist or is already done.")



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
