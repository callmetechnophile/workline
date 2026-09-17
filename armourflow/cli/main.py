"""Authoritative ArmourFlow CLI interface built with Typer and Rich."""

import asyncio
import json
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from armourflow.config.settings import get_settings
from armourflow.config.validation import ConfigurationValidator
from armourflow.data.client import get_database_client
from armourflow.fabric.fabric import get_control_fabric
from armourflow.models.bedrock import get_model_provider
from armourflow.registry.registry import get_agent_registry
from armourflow.security.armoriq import get_security_boundary

app = typer.Typer(
    name="armourflow",
    help="ArmourFlow AI / WorkflowGuide AI Platform CLI",
    add_completion=False,
    no_args_is_help=False,
)
system_app = typer.Typer(help="Platform system status, health, and diagnostics")
agents_app = typer.Typer(help="Agent registry, capability discovery, and health inspection")
project_app = typer.Typer(help="Project graph state and lifecycle tracking")
task_app = typer.Typer(help="Task submission, routing, and lifecycle status")

harness_app = typer.Typer(help="Automated evaluation harness and benchmark verification")
graphql_app = typer.Typer(help="GraphQL API server and schema tooling")

app.add_typer(system_app, name="system")
app.add_typer(agents_app, name="agents")
app.add_typer(project_app, name="project")
app.add_typer(task_app, name="task")
app.add_typer(harness_app, name="harness")
app.add_typer(graphql_app, name="graphql")

console = Console()


def version_callback(value: bool):
    if value:
        settings = get_settings()
        console.print(f"[bold cyan]{settings.app_name}[/] version [bold green]{settings.app_version}[/] ({settings.app_env.value})")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show platform version and exit.", callback=version_callback, is_eager=True
    ),
):
    """ArmourFlow AI — Autonomous Engineering Platform."""
    pass


# ==============================================================================
# SYSTEM COMMANDS
# ==============================================================================

@system_app.command("status")
def system_status():
    """Display high-level operational status of the platform."""
    settings = get_settings()
    fabric = get_control_fabric()
    db = get_database_client()
    models = get_model_provider()
    sec = get_security_boundary()
    reg = get_agent_registry()

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold cyan", justify="right")
    grid.add_column(style="white")

    grid.add_row("Application:", f"{settings.app_name} v{settings.app_version} ({settings.app_env.value})")
    grid.add_row("Control Fabric:", f"{fabric.health_check()['status']} ({len(reg.list_agents())} agents registered)")
    grid.add_row("State Database:", f"{db.health_check()['provider']} ({db.health_check()['status']})")
    grid.add_row("Model Provider:", f"{models.health_check()['provider']} ({models.health_check()['status']} in {models.region})")
    grid.add_row("Authorization:", f"{sec.health_check()['provider']} (Scopes: {sec.health_check()['registered_agent_scopes']})")

    panel = Panel(grid, title="[bold green]ArmourFlow Platform Status[/]", border_style="cyan")
    console.print(panel)


@system_app.command("health")
def system_health():
    """Inspect granular health of all platform subsystems."""
    db = get_database_client()
    models = get_model_provider()
    sec = get_security_boundary()
    fabric = get_control_fabric()

    table = Table(title="Platform Subsystem Health", border_style="cyan")
    table.add_column("Subsystem", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Provider / Component", style="cyan")
    table.add_column("Details", style="dim")

    checks = [
        ("Control Fabric", fabric.health_check()["status"], "AgentControlFabric", f"{fabric.health_check()['registered_agents']} agents"),
        ("State / Graph DB", db.health_check()["status"], db.health_check()["provider"], f"Live: {db.health_check()['live_connection']}"),
        ("Model Provider", models.health_check()["status"], models.health_check()["provider"], f"Model: {models.reasoning_model}"),
        ("Authorization", sec.health_check()["status"], sec.health_check()["provider"], f"Scopes: {sec.health_check()['registered_agent_scopes']}"),
    ]

    for name, status, prov, details in checks:
        color = "green" if status == "HEALTHY" else "yellow"
        table.add_row(name, f"[{color}]{status}[/]", prov, details)

    console.print(table)


@system_app.command("diagnostics")
def system_diagnostics():
    """Run comprehensive configuration and connectivity diagnostics without printing secrets."""
    validator = ConfigurationValidator()
    results = validator.run_diagnostics()

    table = Table(title="System Configuration Diagnostics", border_style="cyan")
    table.add_column("Component", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Diagnostic Detail", style="dim")

    for res in results:
        color = "green" if res.status == "CONFIGURED" else ("yellow" if res.status == "DISABLED" else "red")
        table.add_row(res.name, f"[{color}]{res.status.value}[/]", res.details)

    console.print(table)


# ==============================================================================
# AGENTS COMMANDS
# ==============================================================================

@agents_app.command("list")
def agents_list():
    """List all registered agents, versions, capabilities, and execution levels."""
    reg = get_agent_registry()
    agents = reg.list_agents()

    table = Table(title=f"Authoritative Agent Registry ({len(agents)} Registered)", border_style="cyan")
    table.add_column("ID", style="bold cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Version", justify="center")
    table.add_column("Level", style="magenta")
    table.add_column("Capabilities", style="dim")

    for a in sorted(agents, key=lambda x: x.agent_id):
        caps = ", ".join(a.capabilities[:3]) + (f" (+{len(a.capabilities)-3})" if len(a.capabilities) > 3 else "")
        table.add_row(a.agent_id, a.name, a.version, a.execution_level, caps)

    console.print(table)


@agents_app.command("info")
def agents_info(agent_id: str = typer.Argument(..., help="Agent ID (e.g. 'agent.24', 'agent.01') or name")):
    """Show detailed manifest for a specific agent."""
    reg = get_agent_registry()
    a = reg.get_agent(agent_id)
    if not a:
        console.print(f"[bold red]Error:[/] Agent '{agent_id}' not found in registry.")
        raise typer.Exit(1)

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold cyan", justify="right")
    grid.add_column(style="white")

    grid.add_row("Agent ID:", a.agent_id)
    if a.alias_id:
        grid.add_row("Legacy Alias:", a.alias_id)
    grid.add_row("Name:", a.name)
    grid.add_row("Version:", a.version)
    grid.add_row("Execution Level:", a.execution_level)
    grid.add_row("Entrypoint:", a.entrypoint)
    grid.add_row("Description:", a.description)
    grid.add_row("Dependencies:", ", ".join(a.dependencies) if a.dependencies else "None")
    grid.add_row("Permissions:", ", ".join(a.permissions) if a.permissions else "None")
    grid.add_row("Capabilities:", ", ".join(a.capabilities))

    panel = Panel(grid, title=f"[bold green]Agent Manifest: {a.name}[/]", border_style="cyan")
    console.print(panel)


@agents_app.command("health")
def agents_health():
    """Verify live health and importability of all 27 agents."""
    reg = get_agent_registry()
    agents = reg.list_agents()

    table = Table(title="Agent Live Health Status", border_style="cyan")
    table.add_column("Agent ID", style="bold cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Health", justify="center")
    table.add_column("Importable", justify="center")

    for a in sorted(agents, key=lambda x: x.agent_id):
        h = reg.check_health(a.agent_id)
        is_ok = h["status"] == "HEALTHY"
        color = "green" if is_ok else "red"
        table.add_row(
            a.agent_id,
            a.name,
            f"[{color}]{h['status']}[/]",
            "[green]YES[/]" if h["importable"] else "[red]NO[/]",
        )

    console.print(table)


# ==============================================================================
# PROJECT COMMANDS
# ==============================================================================

@project_app.command("list")
def project_list():
    """List projects stored in the persistent graph state."""
    db = get_database_client()
    projects = asyncio.run(db.list_by_table("project"))

    table = Table(title=f"Projects ({len(projects)} Found)", border_style="cyan")
    table.add_column("Project ID", style="bold cyan")
    table.add_column("Title / Details", style="white")
    table.add_column("Created", style="dim")

    if not projects:
        table.add_row("default", "Default Engineering Project", "System Initialized")
    else:
        for p in projects:
            table.add_row(p.get("id", "UNKNOWN"), p.get("title", "Untitled"), p.get("created_at", "N/A"))

    console.print(table)


@project_app.command("status")
def project_status(project_id: str = typer.Argument("default", help="Project identifier")):
    """View graph state, associated tasks, and lifecycle status for a project."""
    fabric = get_control_fabric()
    tasks = fabric.list_tasks(project_id)

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold cyan", justify="right")
    grid.add_column(style="white")

    grid.add_row("Project ID:", project_id)
    grid.add_row("Associated Tasks:", str(len(tasks)))
    grid.add_row("Completed Tasks:", str(sum(1 for t in tasks if t.state.value == "COMPLETED")))
    grid.add_row("Failed Tasks:", str(sum(1 for t in tasks if t.state.value == "FAILED")))

    panel = Panel(grid, title=f"[bold green]Project Status: {project_id}[/]", border_style="cyan")
    console.print(panel)


# ==============================================================================
# TASK COMMANDS
# ==============================================================================

@task_app.command("create")
def task_create(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Target agent identifier"),
    capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Target capability to route to"),
    project: str = typer.Option("default", "--project", "-p", help="Target project identifier"),
    payload: str = typer.Option("{}", "--payload", help="JSON task payload string or @filepath"),
):
    """Submit a task to the Agent Control Fabric."""
    if not agent and not capability:
        console.print("[bold red]Error:[/] Specify either --agent or --capability.")
        raise typer.Exit(1)

    raw_payload = payload.strip()
    if raw_payload.startswith("@") and os.path.exists(raw_payload[1:]):
        with open(raw_payload[1:], "r", encoding="utf-8") as f:
            raw_payload = f.read()

    try:
        data = json.loads(raw_payload)
    except Exception:
        # Fallback for Windows shells that strip double quotes: try parsing single quotes
        try:
            import ast
            data = ast.literal_eval(raw_payload)
            if not isinstance(data, dict):
                raise ValueError("Payload must be a dictionary")
        except Exception as e:
            console.print(f"[bold red]Error:[/] Invalid JSON payload: {e}")
            raise typer.Exit(1)

    fabric = get_control_fabric()
    task = asyncio.run(
        fabric.submit_task(
            payload=data,
            target_agent_id=agent,
            target_capability=capability,
            project_id=project,
        )
    )

    color = "green" if task.state.value == "COMPLETED" else "red"
    console.print(f"Task ID: [bold cyan]{task.task_id}[/]")
    console.print(f"Target Agent: [bold white]{task.target_agent_id}[/]")
    console.print(f"State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2), title="Result", border_style="green"))


@task_app.command("status")
def task_status(task_id: str = typer.Argument(..., help="Task ID to inspect")):
    """Check lifecycle state and execution output of a submitted task."""
    fabric = get_control_fabric()
    task = fabric.get_task(task_id)
    if not task:
        console.print(f"[bold red]Error:[/] Task '{task_id}' not found.")
        raise typer.Exit(1)

    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"Task: [bold cyan]{task.task_id}[/] | State: [{color}]{task.state.value}[/]")
    console.print(f"Agent: [bold white]{task.target_agent_id}[/] | Project: [dim]{task.context.project_id}[/]")
    if task.result:
        console.print(Panel(json.dumps(task.result, indent=2), title="Task Result", border_style="green"))
    elif task.error:
        console.print(f"[bold red]Error:[/] {task.error}")


# ==============================================================================
# EVALUATION HARNESS COMMANDS
# ==============================================================================

@harness_app.command("run")
def harness_run(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Specific agent ID to evaluate"),
):
    """Execute automated benchmark suites against registered agents."""
    from armourflow.evals import get_evaluation_harness

    harness = get_evaluation_harness()
    if agent:
        console.print(f"Running benchmarks for [bold cyan]{agent}[/]...")
        summary = asyncio.run(harness.evaluate_agent(agent))
        if not summary:
            console.print(f"[bold red]Error:[/] No benchmark suite found for agent '{agent}'.")
            raise typer.Exit(1)

        table = Table(title=f"Benchmark Results: {agent}", border_style="cyan")
        table.add_column("Benchmark Name", style="bold white")
        table.add_column("Category", style="cyan")
        table.add_column("Status", justify="center")

        for b in summary.benchmarks:
            table.add_row(
                b.name,
                b.category,
                "[bold green]PASS[/]" if b.passed else "[bold red]FAIL[/]",
            )
        console.print(table)
        console.print(f"Pass Rate: [bold green]{summary.score_percentage}%[/] ({summary.passed_benchmarks}/{summary.total_benchmarks})")
    else:
        console.print("Running platform-wide benchmark suites...")
        report = asyncio.run(harness.run_platform_benchmarks())

        table = Table(title="Platform Benchmark Evaluation Summary", border_style="cyan")
        table.add_column("Agent ID", style="bold cyan")
        table.add_column("Total Tests", justify="right")
        table.add_column("Passed", justify="right")
        table.add_column("Score", justify="right")

        for aid, s in report.agent_summaries.items():
            color = "green" if s.score_percentage == 100.0 else "yellow"
            table.add_row(
                aid,
                str(s.total_benchmarks),
                str(s.passed_benchmarks),
                f"[{color}]{s.score_percentage}%[/]",
            )
        console.print(table)
        console.print(
            f"Overall Pass Rate: [bold green]{report.overall_pass_rate}%[/] ({report.total_passed}/{report.total_benchmarks} across {report.total_agents_evaluated} evaluated agents)"
        )


# ==============================================================================
# GRAPHQL API COMMANDS
# ==============================================================================

@graphql_app.command("schema")
def graphql_schema():
    """Print the complete GraphQL Schema Definition Language (SDL)."""
    from armourflow.graphql import schema
    console.print(str(schema))


@graphql_app.command("serve")
def graphql_serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host interface to bind"),
    port: int = typer.Option(10000, "--port", "-p", help="Port to listen on"),
    reload: bool = typer.Option(False, "--reload", help="Enable live code reload"),
):
    """Start the ArmourFlow GraphQL and FastAPI API server."""
    import uvicorn
    console.print(f"Starting ArmourFlow GraphQL API server on [bold cyan]http://{host}:{port}/graphql[/]...")
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)


def main():
    app()



if __name__ == "__main__":
    main()
