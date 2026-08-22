"""CLI commands for Component Validation and Candidate Comparison."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer
from backend.workline.validation.models import ValidationStatus
from backend.workline.validation.service import validation_service

app = typer.Typer(name="component", help="Validate and compare engineering component candidates.")
component_app = app
console = Console()


@app.command("validate")
def validate_component_cmd(
    component_id: str = typer.Argument(..., help="Component ID to validate"),
    requirement_id: str = typer.Option(..., "--requirement", "-r", help="Target requirement ID"),
):
    """Validate a component against an engineering requirement."""
    try:
        val = validation_service.validate_candidate(requirement_id, component_id)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    status_color = "green" if val.overall_status == ValidationStatus.PASS else "red" if val.overall_status == ValidationStatus.FAIL else "yellow"
    console.print(
        Panel.fit(
            f"[bold cyan]Component:[/bold cyan] {component_id}\n"
            f"[bold]Requirement:[/bold] {requirement_id}\n"
            f"[bold]Status:[/bold] [{status_color}]{val.overall_status.value}[/{status_color}]\n"
            f"[bold]Constraints Evaluated:[/bold] {len(val.constraint_results)}",
            title="Component Validation Outcome",
            border_style="cyan",
        )
    )


@app.command("compare")
def compare_components_cmd(
    id1: str = typer.Argument(..., help="First candidate component ID"),
    id2: str = typer.Argument(..., help="Second candidate component ID"),
    requirement_id: str = typer.Option(..., "--requirement", "-r", help="Target requirement ID"),
):
    """Compare two candidate components side-by-side against a requirement."""
    val1 = validation_service.validate_candidate(requirement_id, id1)
    val2 = validation_service.validate_candidate(requirement_id, id2)

    table = Table(title=f"CANDIDATE COMPARISON FOR {requirement_id}", border_style="cyan")
    table.add_column("Property", style="bold")
    table.add_column(f"{id1}", style="cyan")
    table.add_column(f"{id2}", style="purple")

    table.add_row("Overall Status", val1.overall_status.value, val2.overall_status.value)
    console.print(table)
