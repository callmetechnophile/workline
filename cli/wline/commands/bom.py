"""BOM generation, inspection, and human approval CLI commands."""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.workline.procurement.engine import procurement_engine
from backend.workline.procurement.models import ComponentRequirement
from cli.wline.core.paths import get_active_project_name
from cli.wline.ui.output import print_error, print_info, print_success, print_warning

bom_app = typer.Typer(name="bom", help="Generate, inspect, and approve engineering Bill of Materials.")
console = Console()


@bom_app.command("generate")
def bom_generate() -> None:
    """Generate engineering BOM with landed cost optimization for active project."""
    active_name = get_active_project_name()
    if not active_name:
        print_error("No active project selected. Run 'wline project open <name>' first.")
        raise typer.Exit(code=1)

    console.print(f"\n[bold cyan]GENERATING BILL OF MATERIALS:[/bold cyan] [bold green]{active_name}[/bold green]\n")

    reqs = [
        ComponentRequirement(requirement_id="req_mcu", category="Microcontroller / Compute Unit", quantity=1),
        ComponentRequirement(requirement_id="req_env", category="Sensors & Environmental", quantity=1),
        ComponentRequirement(requirement_id="req_reg", category="Power Management / Voltage Regulator", quantity=2),
        ComponentRequirement(requirement_id="req_drv", category="Actuator Driver / Motor Control", quantity=1),
        ComponentRequirement(requirement_id="req_soil", category="Sensors & Environmental", quantity=1),
    ]

    bom, _ = asyncio.run(procurement_engine.generate_project_bom(active_name, reqs))

    print_success(f"BOM Generated ({bom.status.value}) — {len(bom.items)} Line Items")
    _render_bom_table(bom)


@bom_app.command("status")
def bom_status(
    bom_id: Optional[str] = typer.Argument(None, help="BOM ID or Project ID (defaults to active project)")
) -> None:
    """Display current BOM status and item breakdown."""
    target_id = bom_id or get_active_project_name()
    if not target_id:
        print_error("No active project. Specify a project or BOM ID.")
        raise typer.Exit(code=1)

    bom = asyncio.run(procurement_engine.get_bom(target_id))
    if not bom:
        print_warning(f"No BOM found for '{target_id}'. Run 'wline bom generate' first.")
        return

    _render_bom_table(bom)


@bom_app.command("approve")
def bom_approve(
    bom_id: Optional[str] = typer.Argument(None, help="BOM ID or Project ID to approve"),
    reviewer: str = typer.Option("Lead Engineer", "--by", "-b", help="Reviewer name / title"),
) -> None:
    """Human approval action transitioning BOM from READY_FOR_REVIEW to APPROVED."""
    target_id = bom_id or get_active_project_name()
    if not target_id:
        print_error("No active project specified.")
        raise typer.Exit(code=1)

    approved = asyncio.run(procurement_engine.approve_bom(target_id, approved_by=reviewer))
    if not approved:
        print_error(f"Could not approve BOM for '{target_id}'.")
        raise typer.Exit(code=1)

    print_success(f"BOM '{approved.bom_id}' has been APPROVED by {reviewer}!")
    _render_bom_table(approved)


def _render_bom_table(bom) -> None:
    status_color = "green" if bom.status.value == "APPROVED" else "yellow"
    console.print(f"\n[bold white]BOM ID:[/bold white]       {bom.bom_id}")
    console.print(f"[bold white]Status:[/bold white]       [{status_color}]{bom.status.value}[/{status_color}]")
    console.print(f"[bold white]Component Cost:[/bold white] INR {bom.total_component_cost}")
    console.print(f"[bold white]Est. Shipping:[/bold white]  INR {bom.estimated_shipping} (ESTIMATED)")
    console.print(f"[bold white]Landed Total:[/bold white]   [bold green]INR {bom.estimated_total}[/bold green]\n")

    table = Table(box=None)
    table.add_column("Component", style="bold cyan")
    table.add_column("MPN", style="white")
    table.add_column("Qty", style="magenta")
    table.add_column("Vendor", style="yellow")
    table.add_column("Unit Price", style="white")
    table.add_column("Ext. Price", style="bold green")
    table.add_column("Datasheet", style="dim")

    for item in bom.items:
        table.add_row(
            item.description[:24] if item.description else item.mpn,
            item.mpn,
            str(item.quantity),
            item.selected_vendor,
            f"INR {item.unit_price}",
            f"INR {item.extended_price}",
            "VERIFIED" if item.datasheet_url else "N/A",
        )

    console.print(table)
    console.print()
