"""
wline system - Platform health, status, version, and configuration diagnostics.

Aggregates data from Control Fabric, database client, model provider,
security boundary, and all 13 configuration validators into clear
Rich-formatted tables or pure JSON.
"""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cli.wline import __version__
from cli.wline.core.errors import print_json_output, exit_with_error, ExitCode

system_app = typer.Typer(
    name="system",
    help="Platform health, status, version, and configuration diagnostics.",
)
console = Console()


def _platform_singletons():
    from armourflow.config.settings import get_settings
    from armourflow.fabric.fabric import get_control_fabric
    from armourflow.data.client import get_database_client
    from armourflow.models.bedrock import get_model_provider
    from armourflow.security.armoriq import get_security_boundary
    from armourflow.registry.registry import get_agent_registry
    return (
        get_settings(),
        get_control_fabric(),
        get_database_client(),
        get_model_provider(),
        get_security_boundary(),
        get_agent_registry(),
    )


@system_app.command("health")
def system_health(
    json_output: bool = typer.Option(False, "--json", help="Output health metrics as pure JSON"),
):
    """Show live health status of all platform components."""
    try:
        settings, fabric, db, models, sec, reg = _platform_singletons()

        fabric_h = fabric.health_check()
        db_h = db.health_check()
        models_h = models.health_check()
        sec_h = sec.health_check()
        agents = reg.list_agents()
    except Exception as e:
        exit_with_error(f"Failed to gather system health: {e}", ExitCode.SERVICE_UNAVAILABLE, json_mode=json_output)

    checks = [
        {
            "component": "Control Fabric",
            "status": fabric_h.get("status", "UNKNOWN"),
            "provider": "AgentControlFabric",
            "details": f"{fabric_h.get('registered_agents', len(agents))} agents registered",
        },
        {
            "component": "State / Graph DB",
            "status": db_h.get("status", "UNKNOWN"),
            "provider": db_h.get("provider", "SurrealDB / InMemory"),
            "details": f"Live connection: {db_h.get('live_connection', False)}",
        },
        {
            "component": "Model Provider",
            "status": models_h.get("status", "UNKNOWN"),
            "provider": models_h.get("provider", "Amazon Bedrock"),
            "details": f"Reasoning model: {getattr(models, 'reasoning_model', 'N/A')}",
        },
        {
            "component": "Authorization",
            "status": sec_h.get("status", "UNKNOWN"),
            "provider": sec_h.get("provider", "ArmorIQ"),
            "details": f"Scopes: {sec_h.get('registered_agent_scopes', 0)}",
        },
        {
            "component": "Agent Registry",
            "status": "HEALTHY" if len(agents) == 27 else ("DEGRADED" if agents else "UNKNOWN"),
            "provider": "AuthoritativeAgentRegistry",
            "details": f"{len(agents)} domain agents indexed",
        },
    ]

    if json_output:
        overall_status = "HEALTHY" if all(c["status"] == "HEALTHY" for c in checks) else "DEGRADED"
        print_json_output({
            "overall_status": overall_status,
            "components": checks,
        })
        return

    table = Table(title="WORKLINE Platform Health", border_style="cyan")
    table.add_column("Component", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Provider / Component", style="cyan")
    table.add_column("Details", style="dim")

    for item in checks:
        status = item["status"]
        color = "green" if status == "HEALTHY" else ("yellow" if status == "DEGRADED" else "red")
        table.add_row(item["component"], f"[{color}]{status}[/]", item["provider"], item["details"])

    console.print(table)


@system_app.command("status")
def system_status(
    json_output: bool = typer.Option(False, "--json", help="Output platform status as pure JSON"),
):
    """Display platform version, environment, and key configuration summary."""
    try:
        settings, fabric, db, models, sec, reg = _platform_singletons()
        env = getattr(settings, "environment", getattr(settings, "ENVIRONMENT", "development"))
        fabric_h = fabric.health_check()
        agent_count = len(reg.list_agents())
    except Exception as e:
        exit_with_error(f"Failed to inspect system status: {e}", ExitCode.SERVICE_UNAVAILABLE, json_mode=json_output)

    status_data = {
        "platform": "WORKLINE / ArmourFlow AI",
        "cli_version": __version__,
        "environment": str(env),
        "registered_agents": agent_count,
        "control_fabric": "AgentControlFabric (Google ADK / A2A / Bindu)",
        "state_layer": "SurrealDB (graph) + Qdrant (vector)",
        "model_provider": "Amazon Bedrock",
        "authorization": "ArmorIQ",
        "api_layers": ["FastAPI REST", "GraphQL (Strawberry) at /graphql"],
        "pending_tasks": fabric_h.get("pending_tasks", 0),
    }

    if json_output:
        print_json_output(status_data)
        return

    title = Text()
    title.append("WORKLINE / ArmourFlow AI\n", style="bold cyan")
    title.append("Engineering Lifecycle Platform", style="dim white")

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold cyan", justify="right")
    grid.add_column(style="white")

    grid.add_row("Platform:", status_data["platform"])
    grid.add_row("CLI Version:", status_data["cli_version"])
    grid.add_row("Environment:", status_data["environment"])
    grid.add_row("Registered Agents:", str(status_data["registered_agents"]))
    grid.add_row("Control Fabric:", status_data["control_fabric"])
    grid.add_row("State Layer:", status_data["state_layer"])
    grid.add_row("Model Provider:", status_data["model_provider"])
    grid.add_row("Authorization:", status_data["authorization"])
    grid.add_row("API Layers:", ", ".join(status_data["api_layers"]))
    grid.add_row("Pending Tasks:", str(status_data["pending_tasks"]))

    console.print(Panel(grid, title=title, border_style="cyan"))


@system_app.command("version")
def system_version(
    json_output: bool = typer.Option(False, "--json", help="Output version info as pure JSON"),
):
    """Display WORKLINE CLI and platform version details."""
    version_info = {
        "cli_version": __version__,
        "platform": "WORKLINE Engineering Lifecycle Platform",
        "protocol_version": "1.0.0",
        "agents_schema_version": "1.0.0",
    }
    if json_output:
        print_json_output(version_info)
    else:
        console.print(f"[bold cyan]WORKLINE CLI version:[/] [bold green]{__version__}[/]")
        console.print(f"[dim]Protocol:[/] 1.0.0 | [dim]Schema:[/] 1.0.0")


@system_app.command("diagnostics")
def system_diagnostics(
    json_output: bool = typer.Option(False, "--json", help="Output diagnostics as pure JSON"),
):
    """Run the 13-checkpoint configuration and connectivity diagnostics."""
    from armourflow.config.validation import ConfigurationValidator

    validator = ConfigurationValidator()
    results = validator.run_diagnostics()

    if json_output:
        items = []
        for res in results:
            status_val = res.status.value if hasattr(res.status, "value") else str(res.status)
            items.append({
                "name": res.name,
                "status": status_val,
                "details": res.details,
            })
        print_json_output({"diagnostics": items})
        return

    table = Table(title="System Configuration Diagnostics (13 Checks)", border_style="cyan")
    table.add_column("Component", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Diagnostic Detail", style="dim")

    ok_count = 0
    for res in results:
        status_val = res.status.value if hasattr(res.status, "value") else str(res.status)
        if status_val == "CONFIGURED":
            color = "green"
            ok_count += 1
        elif status_val == "DISABLED":
            color = "yellow"
        else:
            color = "red"
        table.add_row(res.name, f"[{color}]{status_val}[/]", res.details)

    console.print(table)
    total = len(results)
    console.print(
        f"\n[bold]Diagnostics: [{('green' if ok_count == total else 'yellow')}]{ok_count}/{total} CONFIGURED[/][/bold]"
    )
