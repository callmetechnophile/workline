"""CLI commands for Requirement definition and validation."""

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    RequirementCategory,
    ValidationStatus,
)
from backend.workline.validation.service import validation_service

app = typer.Typer(name="requirement", help="Create, inspect, and evaluate engineering requirements.")
requirement_app = app
console = Console()


@app.command("create")
def create_requirement_cmd(
    req_id: str = typer.Argument(None, help="Unique requirement ID"),
    description: str = typer.Argument(None, help="Requirement text / description"),
    title: str = typer.Option(None, "--title", "-t", help="Requirement title"),
    value: str = typer.Option(None, "--value", "-v", help="Numerical value"),
    unit: str = typer.Option(None, "--unit", "-u", help="Unit symbol"),
    project_id: str = typer.Option("rover_v2", "--project", "-p", help="Target project ID"),
    category: str = typer.Option("ELECTRICAL", "--category", "-c", help="Requirement category"),
):
    """Create a new engineering requirement."""
    final_id = req_id or f"REQ-{int(time.time() * 1000)}"
    final_desc = description or title or "Engineering requirement"
    if value and unit:
        final_desc = f"{final_desc}: {value} {unit}"

    req = validation_service.create_requirement(
        requirement_id=final_id,
        project_id=project_id,
        description=final_desc,
        category=RequirementCategory(category.upper()) if category.upper() in RequirementCategory.__members__ else RequirementCategory.ELECTRICAL,
    )
    console.print(f"[bold green]✓ Requirement created successfully: '{req.requirement_id}'[/bold green]")


@app.command("list")
def list_requirements_cmd(
    project_id: str = typer.Option(None, "--project", "-p", help="Filter by project ID"),
):
    """List all project requirements."""
    reqs = validation_service.list_requirements(project_id)
    table = Table(title="PROJECT REQUIREMENTS", border_style="cyan")
    table.add_column("Requirement ID", style="bold cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Description")
    table.add_column("Constraints")
    table.add_column("Priority")

    for r in reqs:
        table.add_row(
            r.requirement_id,
            r.category.value,
            r.description,
            str(len(r.constraints)),
            r.priority,
        )

    console.print(table)


@app.command("inspect")
def inspect_requirement_cmd(
    requirement_id: str = typer.Argument(..., help="Requirement ID to inspect"),
):
    """Inspect constraints and metadata for a requirement."""
    req = validation_service.get_requirement(requirement_id)
    if not req:
        console.print(f"[red]Error: Requirement '{requirement_id}' not found[/red]")
        raise typer.Exit(1)

    console.print(
        Panel.fit(
            f"[bold cyan]ID:[/bold cyan] {req.requirement_id}\n"
            f"[bold]Category:[/bold] {req.category.value}\n"
            f"[bold]Description:[/bold] {req.description}\n"
            f"[bold]Priority:[/bold] {req.priority}\n"
            f"[bold]Constraints Count:[/bold] {len(req.constraints)}",
            title="Engineering Requirement",
            border_style="cyan",
        )
    )

    if req.constraints:
        table = Table(title="CONSTRAINTS", border_style="green")
        table.add_column("Property", style="bold")
        table.add_column("Operator", style="yellow")
        table.add_column("Required Value", style="green")
        table.add_column("Dimension")
        for c in req.constraints:
            table.add_row(c.property, c.operator.value, c.required_value, c.dimension)
        console.print(table)


@app.command("validate")
def validate_requirement_cmd(
    requirement_id: str = typer.Argument(..., help="Requirement ID to validate"),
    candidate_id: str = typer.Option("ENT-TPS62130", "--candidate", "-c", help="Candidate component ID"),
):
    """Deterministically evaluate a candidate component against the requirement."""
    try:
        val = validation_service.validate_candidate(requirement_id, candidate_id)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    console.print(Panel.fit(f"[bold cyan]WORKLINE ENGINEERING VALIDATION[/bold cyan]\nRequirement: [bold]{requirement_id}[/bold]\nCandidate: [bold]{candidate_id}[/bold]"))

    table = Table(title="CONSTRAINT EVALUATION BREAKDOWN", border_style="cyan")
    table.add_column("Property", style="bold")
    table.add_column("Required", style="yellow")
    table.add_column("Actual", style="green")
    table.add_column("Status")
    table.add_column("Reason")

    for cr in val.constraint_results:
        color = "green" if cr.status == ValidationStatus.PASS else "red" if cr.status == ValidationStatus.FAIL else "yellow"
        table.add_row(
            cr.property,
            cr.required_value,
            cr.actual_value,
            f"[{color}]{cr.status.value}[/{color}]",
            cr.reason,
        )

    console.print(table)

    status_color = "green" if val.overall_status == ValidationStatus.PASS else "red" if val.overall_status == ValidationStatus.FAIL else "yellow"
    console.print(f"\n[bold]OVERALL RESULT:[/bold] [{status_color}]{val.overall_status.value}[/{status_color}]")
    console.print(f"Rule Version: {val.rule_version} | Knowledge Version: {val.knowledge_version}")
