"""
wline security - Platform security audit and threat scanning commands.

Routes to agent.22 (SecurityThreatAgent) via the AgentControlFabric and
ArmorIQ boundary for compliance-level enforcement. The ArmorIQ
boundary provides scope enforcement; agent.22 provides threat modelling.
"""

import asyncio
import json
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.wline.ui.output import print_error, print_info

security_app = typer.Typer(
    name="security",
    help="Security audit and threat scanning via ArmorIQ and agent.22.",
)
console = Console()


def _fabric():
    from armourflow.fabric.fabric import get_control_fabric
    return get_control_fabric()


def _armoriq():
    from armourflow.security.armoriq import get_security_boundary
    return get_security_boundary()


@security_app.command("audit")
def security_audit(
    scope: str = typer.Option("full", "--scope", "-s", help="Audit scope: full | agent | project"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="Additional audit parameters as JSON"),
):
    """Run a full platform security and compliance audit."""
    try:
        extra = json.loads(payload)
    except json.JSONDecodeError:
        print_error("--payload must be valid JSON.")
        raise typer.Exit(1)

    # First: ArmorIQ boundary health
    sec = _armoriq()
    sec_health = sec.health_check()

    console.print(f"[bold cyan]Security Audit[/] → ArmorIQ + agent.22")
    console.print(f"  Scope: [bold white]{scope}[/]  Project: [dim]{project}[/]")

    # ArmorIQ status table
    table = Table(title="ArmorIQ Security Boundary", border_style="cyan", show_header=False)
    table.add_column(style="bold cyan", justify="right")
    table.add_column(style="white")

    color = "green" if sec_health.get("status") == "HEALTHY" else "red"
    table.add_row("Status:", f"[{color}]{sec_health.get('status', 'UNKNOWN')}[/]")
    table.add_row("Provider:", sec_health.get("provider", "ArmorIQ"))
    table.add_row("Registered Scopes:", str(sec_health.get("registered_agent_scopes", 0)))
    console.print(table)

    # Submit threat audit task
    data = {"scope": scope, "project_id": project, **extra}
    fabric = _fabric()
    task = asyncio.run(
        fabric.submit_task(
            payload=data,
            target_agent_id="agent.22",
            target_capability="security_threat_analysis",
            project_id=project,
        )
    )

    task_color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"\nAudit Task: [bold cyan]{task.task_id}[/]  State: [{task_color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Audit Report", border_style="green"))


@security_app.command("scan")
def security_scan(
    target: str = typer.Option("platform", "--target", "-t", help="Scan target: platform | agent.<id> | component name"),
    threat_model: str = typer.Option("STRIDE", "--model", "-m", help="Threat modelling framework: STRIDE | PASTA | DREAD"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
):
    """Run a targeted threat scan on a specific component or agent."""
    console.print(f"[bold cyan]Security Threat Scan[/] → agent.22  [{threat_model}]")
    console.print(f"  Target: [bold white]{target}[/]")

    fabric = _fabric()
    task = asyncio.run(
        fabric.submit_task(
            payload={"target": target, "threat_model": threat_model},
            target_agent_id="agent.22",
            target_capability="security_threat_analysis",
            project_id=project,
        )
    )

    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"Task: [bold cyan]{task.task_id}[/]  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Threat Scan Report", border_style="green"))
