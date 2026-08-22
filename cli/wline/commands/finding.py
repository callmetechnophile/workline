"""Finding management CLI commands."""

import secrets
from typing import Optional
from rich.console import Console
from rich.table import Table
import typer

from backend.workline.knowledge import (
    Actor,
    ActorType,
    EngineeringFinding,
    FindingSeverity,
    FindingStatus,
    knowledge_service,
)
from cli.wline.core.paths import get_active_project_name

finding_app = typer.Typer(name="finding", help="Manage engineering findings, anomalies, and validation failures.")
console = Console()


@finding_app.command("create")
def create_finding_cmd(
    title: str = typer.Option(..., "--title", "-t", help="Finding summary."),
    description: str = typer.Option(..., "--description", "-d", help="Detailed description."),
    category: str = typer.Option("THERMAL", "--category", "-c", help="Domain category."),
    severity: str = typer.Option("HIGH", "--severity", "-s", help="Severity (CRITICAL, HIGH, MEDIUM, LOW)."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """Record a new engineering finding."""
    target_project = project or get_active_project_name() or "default_project"
    sev_enum = FindingSeverity[severity.upper()] if severity.upper() in FindingSeverity.__members__ else FindingSeverity.HIGH
    fid = f"FIND-{secrets.token_hex(2).upper()}"

    finding = EngineeringFinding(
        finding_id=fid,
        project_id=target_project,
        title=title,
        description=description,
        category=category.upper(),
        severity=sev_enum,
        source="CLI",
        status=FindingStatus.OPEN,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="cli_user"),
    )

    created = knowledge_service.create_finding(finding)
    console.print(f"\n[bold yellow][OK] Finding recorded:[/bold yellow] [bold cyan]{created.finding_id}[/bold cyan] ({created.title})\n")


@finding_app.command("list")
def list_findings_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """List recorded engineering findings."""
    target_project = project or get_active_project_name() or "default_project"
    findings = knowledge_service.list_findings(target_project)

    if not findings:
        console.print(f"\n[dim]No findings recorded for project '{target_project}'.[/dim]\n")
        return

    table = Table(title=f"Engineering Findings ({target_project})", border_style="yellow")
    table.add_column("Finding ID", style="bold yellow")
    table.add_column("Title")
    table.add_column("Severity")
    table.add_column("Status")

    for f in findings:
        table.add_row(f.finding_id, f.title, f.severity.value, f.status.value)

    console.print(table)
